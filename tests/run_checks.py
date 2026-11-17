#!/usr/bin/env python3
"""Deterministic integration/regression checks. Does not evaluate model activation."""
import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from importlib.metadata import version

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'source/certification-study-simulator'
spec=importlib.util.spec_from_file_location('engine',SKILL/'scripts/engine.py')
e=importlib.util.module_from_spec(spec); spec.loader.exec_module(e)
BANK=e.load(SKILL/'examples/aws-clf-c02-bank.private.json')
BP=e.load(SKILL/'examples/aws-clf-c02-blueprint.json')
PROFILE=e.load(SKILL/'examples/student-profile.json')
ANSWERS=e.load(ROOT/'tests/fixtures/answers.json')
EXPECT=e.load(ROOT/'tests/evaluator/expected.json')

def event(s,action,payload=None,event_id=None):
    return e.record('event',event_id=event_id or 'event-'+str(s['revision']),expected_revision=s['revision'],action=action,payload=payload or {},at=None)

def answer(s,qid,value,bank=BANK):
    return e.apply_event(s,bank,event(s,'answer',{'question_id':qid,'answer':value,'confidence':None}))

def completed():
    s=e.start(BANK,BP,session_id='synthetic-reference')
    for qid in s['question_ids']: s=answer(s,qid,ANSWERS[qid])
    return e.apply_event(s,BANK,event(s,'submit'))

class Checks(unittest.TestCase):
    def test01_frontmatter_and_local_resources(self):
        import yaml
        content=(SKILL/'SKILL.md').read_text()
        fm=yaml.safe_load(content.split('---',2)[1])
        self.assertEqual(set(fm),{'name','description'})
        self.assertEqual(fm['name'],SKILL.name)
        self.assertLess(len(content.splitlines()),250)
        for relative in re.findall(r'\]\(([^)]+)\)',content):
            if not relative.startswith('https://'): self.assertTrue((SKILL/relative).is_file(),relative)

    def test02_schema_and_examples(self):
        from jsonschema import Draft202012Validator
        Draft202012Validator.check_schema(e.load(SKILL/'schemas/contracts.schema.json'))
        for path,kind in [('aws-clf-c02-bank.private.json','question_bank'),('aws-clf-c02-blueprint.json','blueprint'),('student-profile.json','student_profile'),('short-answer.private.json','question')]:
            e.validate(e.load(SKILL/'examples'/path),kind)

    def test03_duplicates_missing_keys_and_wrong_counts(self):
        for mutate in [lambda q:q['options'][1].update(text='  '+q['options'][0]['text'].upper()+'  '),lambda q:q.update(correct_answers=[]),lambda q:q.update(selection_count=2),lambda q:q.update(correct_answers=['Z'])]:
            q=copy.deepcopy(BANK['questions'][0]); mutate(q)
            with self.assertRaises(e.ContractError): e.validate(q,'question')
        b=copy.deepcopy(BANK); b['questions'][1]['stem']=b['questions'][0]['stem']
        with self.assertRaises(e.ContractError): e.validate(b,'question_bank')

    def test04_blueprint_distribution_and_interleaving(self):
        s=e.start(BANK,BP)
        self.assertEqual(s['distribution'],EXPECT['distribution'])
        self.assertEqual(len(set(s['question_ids'])),10)
        self.assertEqual([e.bank_map(BANK)[i]['domain'] for i in s['question_ids'][:4]],['D1','D2','D3','D4'])
        scoped=copy.deepcopy(BP); scoped['domains']=[scoped['domains'][1]]; scoped['domains'][0]['weight']=100
        self.assertEqual(e.start(BANK,scoped,count=3)['distribution'],{'D2':3})

    def test05_mock_projection_and_early_feedback_block(self):
        s=e.start(BANK,BP)
        s=answer(s,'CLF-P001',['A'])
        for projection in (e.view(s,BANK),e.checkpoint(s,BANK)):
            raw=json.dumps(projection)
            for name in EXPECT['forbidden_public_fields']: self.assertNotIn('"'+name+'"',raw)
        with self.assertRaises(e.ContractError): e.report(s,BANK)
        with self.assertRaises(e.ContractError): e.feedback(s,BANK,'CLF-P001')

    def test06_review_revise_flag_skip_and_freeze(self):
        s=e.start(BANK,BP)
        s=answer(s,'CLF-P001',['B'])
        s=e.apply_event(s,BANK,event(s,'goto',{'question_id':'CLF-P001'}))
        self.assertEqual(e.view(s,BANK)['position'],1)
        s=e.apply_event(s,BANK,event(s,'flag',{'question_id':'CLF-P001'}))
        s=answer(s,'CLF-P001',['A']); s=answer(s,'CLF-P002',None)
        s=e.apply_event(s,BANK,event(s,'submit'))
        r=e.report(s,BANK)
        self.assertEqual(r['metrics']['correct'],1); self.assertEqual(r['metrics']['unanswered'],9)
        with self.assertRaises(e.ContractError): answer(s,'CLF-P001',['B'])

    def test07_exact_multiple_and_invalid_input(self):
        s=e.start(BANK,BP)
        for invalid in [['B'],['B','D','E'],['B','B'],['Z','D'],'B,D']:
            with self.assertRaises(e.ContractError): answer(s,'CLF-P003',invalid)
        s=answer(s,'CLF-P003',['D','B'])
        s=e.apply_event(s,BANK,event(s,'submit'))
        self.assertEqual(e.feedback(s,BANK,'CLF-P003')['earned'],1)

    def test08_ten_questions_correctness_domains(self):
        r=e.report(completed(),BANK)
        self.assertEqual(r['metrics']['earned'],EXPECT['reference_score'])
        self.assertEqual(r['metrics']['possible'],EXPECT['reference_total'])
        self.assertEqual(r['metrics']['percentage'],EXPECT['reference_percentage'])
        self.assertEqual({k:v['correct'] for k,v in r['by_domain'].items()},EXPECT['correct_by_domain'])
        self.assertEqual(sum(m['earned'] for m in r['by_subdomain'].values()),7)
        e.verify_report(r)

    def test09_idempotency_revision_guards(self):
        s=e.start(BANK,BP)
        ev=event(s,'answer',{'question_id':'CLF-P001','answer':['A'],'confidence':None},'replay')
        t=e.apply_event(s,BANK,ev)
        self.assertEqual(e.apply_event(t,BANK,ev),t)
        bad=copy.deepcopy(ev); bad['payload']['answer']=['B']
        with self.assertRaises(e.ContractError): e.apply_event(t,BANK,bad)
        old=event(s,'next',event_id='new')
        with self.assertRaises(e.ContractError): e.apply_event(t,BANK,old)

    def test10_guided_feedback_and_no_rewrite(self):
        s=e.start(BANK,BP,mode='guided')
        with self.assertRaises(e.ContractError): e.feedback(s,BANK,'CLF-P001')
        s=answer(s,'CLF-P001',['A'])
        self.assertEqual(e.feedback(s,BANK,'CLF-P001')['outcome'],'correct')
        with self.assertRaises(e.ContractError): answer(s,'CLF-P001',['B'])

    def test11_open_rubric_pending_partial_and_limits(self):
        q=e.load(SKILL/'examples/short-answer.private.json'); b=e.record('question_bank',bank_id='open-demo',questions=[q])
        bp=copy.deepcopy(BP); bp['domains']=[bp['domains'][1]]; bp['domains'][0]['weight']=100
        s=e.start(b,bp,count=1); s=answer(s,q['question_id'],'O cliente atualiza o SO; não sei a parte física.',b)
        grade=dict(evaluator='synthetic-grader',estimated=True,criteria=[dict(criterion_id='guest-os',awarded=1,evidence='O cliente atualiza o SO'),dict(criterion_id='physical',awarded=0,evidence='não sei a parte física')])
        with self.assertRaises(e.ContractError): e.apply_event(s,b,event(s,'grade_open',{'question_id':q['question_id'],'grade':grade}))
        s=e.apply_event(s,b,event(s,'submit'))
        self.assertTrue(e.report(s,b)['provisional']); self.assertIsNone(e.report(s,b)['metrics']['percentage'])
        s=e.apply_event(s,b,event(s,'grade_open',{'question_id':q['question_id'],'grade':grade}))
        self.assertEqual(e.report(s,b)['metrics']['percentage'],50)
        bad=copy.deepcopy(grade); bad['criteria'][0]['awarded']=2
        with self.assertRaises(e.ContractError): e.apply_event(s,b,event(s,'grade_open',{'question_id':q['question_id'],'grade':bad}))

    def test12_challenge_annulment_zero_denominator(self):
        s=e.start(BANK,BP)
        s=e.apply_event(s,BANK,event(s,'challenge',{'question_id':'CLF-P002','reason':'Cenário contestado; conferir fonte.'}))
        with self.assertRaises(e.ContractError): e.apply_event(s,BANK,event(s,'resolve',{'question_id':'CLF-P002','decision':'uphold','reason':'Fonte conferida.'}))
        for qid in s['question_ids']: s=answer(s,qid,ANSWERS[qid])
        s=e.apply_event(s,BANK,event(s,'submit'))
        self.assertEqual(e.report(s,BANK)['metrics']['percentage'],77.78)
        self.assertTrue(e.report(s,BANK)['provisional'])
        s=e.apply_event(s,BANK,event(s,'resolve',{'question_id':'CLF-P002','decision':'void','reason':'Anulação sintética para testar denominador.'}))
        self.assertFalse(e.report(s,BANK)['provisional'])
        for qid in s['question_ids']:
            if qid not in s['voided']: s=e.apply_event(s,BANK,event(s,'challenge',{'question_id':qid,'reason':'Contestação sintética.'}))
        r=e.report(s,BANK)
        self.assertEqual(r['metrics']['possible'],0); self.assertIsNone(r['metrics']['percentage'])
        self.assertFalse(e.recommend(r,'2026-11-16')['priorities'])

    def test13_plan_time_budget_and_deadline(self):
        p=e.plan(PROFILE,BP,'2026-11-16')
        self.assertEqual(p['total_minutes'],EXPECT['plan_total_minutes'])
        self.assertEqual(len(p['weeks']),4)
        self.assertTrue(all(w['available_minutes']==360 for w in p['weeks']))
        with self.assertRaises(e.ContractError): e.plan(PROFILE,BP,PROFILE['target_date'])
        part=copy.deepcopy(PROFILE); part['target_date']='2026-11-19'
        self.assertEqual(e.plan(part,BP,'2026-11-16')['total_minutes'],154)

    def test14_adaptive_priorities_history_and_small_samples(self):
        r=e.report(completed(),BANK); rec=e.recommend(r,'2026-11-16')
        self.assertEqual(sorted(p['objective'] for p in rec['priorities']),EXPECT['weak_objectives'])
        self.assertTrue(all(p['next_difficulty']=='unchanged' for p in rec['priorities']))
        self.assertEqual(rec['priorities'][0]['review_dates'][0],'2026-11-17')
        history=e.record('attempt_history',student_id='demo',attempts=[r])
        self.assertEqual(len(e.compare_history(history)),1)
        with self.assertRaises(e.ContractError): e.start(BANK,BP,seen_ids=list(ANSWERS))
        r2=copy.deepcopy(r); r2['session_id']='second'; r2['exam_code']='OTHER'
        history['attempts'].append(r2)
        self.assertEqual(len(e.compare_history(history)),2)
        # Same engine performs adaptive selection on a larger synthetic reviewed pool.
        b=copy.deepcopy(BANK)
        for q in BANK['questions']:
            new=copy.deepcopy(q); new['question_id']+='-alt'; new['stem']+=' Considere o cenário descrito.'; b['questions'].append(new)
        s=e.start(b,BP,mode='adaptive',count=10,recommendations=rec)
        self.assertEqual(len(s['question_ids']),10)

    def test15_unknown_retired_unavailable_and_unreviewed(self):
        for status in ['retired','unavailable','unverified']:
            bp=copy.deepcopy(BP); bp['status']=status
            with self.assertRaises(e.ContractError): e.start(BANK,bp)
        bp=copy.deepcopy(BP); bp['exam_code']='UNRECOGNIZED'
        with self.assertRaises(e.ContractError): e.start(BANK,bp)
        for status in ['draft','ambiguous','contested']:
            b=copy.deepcopy(BANK); b['questions'][0]['review_status']=status
            with self.assertRaises(e.ContractError): e.start(b,BP)
        q=copy.deepcopy(BANK['questions'][0]); q['source_references'][0]['update_status']='unavailable'
        with self.assertRaises(e.ContractError): e.validate(q,'question')

    def test16_roundtrip_context_loss_and_bank_hash(self):
        s=e.start(BANK,BP); s=answer(s,'CLF-P001',['A'])
        recovered=json.loads(json.dumps(e.checkpoint(s,BANK)))['session']
        self.assertEqual(e.view(s,BANK),e.view(recovered,BANK))
        b=copy.deepcopy(BANK); b['questions'][0]['explanation']+=' Mudou.'
        with self.assertRaises(e.ContractError): e.validate_session(s,b)

    def test17_portable_exports_and_formula_neutralization(self):
        with tempfile.TemporaryDirectory() as td:
            r=e.report(completed(),BANK); dest=Path(td)/'export'
            e.export_report(r,dest)
            self.assertEqual(e.load(dest/'report.json'),r)
            import csv
            self.assertEqual(len(list(csv.DictReader((dest/'responses.csv').open()))),10)
            self.assertIn('70.0%',(dest/'report.md').read_text())
            with self.assertRaises(e.ContractError): e.export_report(r,dest)
            self.assertTrue(e.csv_safe('=1+1').startswith("'"))
            self.assertTrue(e.csv_safe('  @SUM(1)').startswith("'"))

    def test18_bad_json_new_contract_and_report_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            for value in ['{"x":1,"x":2}','{"x":NaN}']:
                p=Path(td)/'bad.json'; p.write_text(value)
                with self.assertRaises(e.ContractError): e.load(p)
        s=e.start(BANK,BP); s['schema_version']='9.0'
        with self.assertRaises(e.ContractError): e.validate_session(s,BANK)
        r=e.report(completed(),BANK); r['metrics']['earned']=99
        with self.assertRaises(e.ContractError): e.verify_report(r)
        self.assertIn('dados não confiáveis',(SKILL/'SKILL.md').read_text())
        # Static safety marker is not a model prompt-injection test.

    def test19_cli_end_to_end_and_private_projection(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td); session=td/'r0.json'
            def cli(*args):
                p=subprocess.run([sys.executable,str(SKILL/'scripts/engine.py'),*map(str,args)],capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                return json.loads(p.stdout)
            cli('start','--bank',SKILL/'examples/aws-clf-c02-bank.private.json','--blueprint',SKILL/'examples/aws-clf-c02-blueprint.json','--out',session)
            for number,qid in enumerate(e.load(session)['question_ids'],1):
                s=e.load(session); ev=event(s,'answer',{'question_id':qid,'answer':ANSWERS[qid],'confidence':None})
                ef=td/f'e{number}.json'; e.write_new(ef,ev); nxt=td/f'r{number}.json'
                out=cli('apply','--bank',SKILL/'examples/aws-clf-c02-bank.private.json','--session',session,'--event',ef,'--out',nxt)
                self.assertNotIn('correct_answers',json.dumps(out)); session=nxt
            ef=td/'submit.json'; e.write_new(ef,event(e.load(session),'submit')); nxt=td/'final.json'
            cli('apply','--bank',SKILL/'examples/aws-clf-c02-bank.private.json','--session',session,'--event',ef,'--out',nxt)
            result=cli('report','--bank',SKILL/'examples/aws-clf-c02-bank.private.json','--session',nxt,'--outdir',td/'result')
            self.assertEqual(result['metrics']['percentage'],70)

    def test20_isolated_runtime_and_missing_dependency(self):
        import shutil
        with tempfile.TemporaryDirectory() as td:
            isolated=Path(td)/SKILL.name; shutil.copytree(SKILL,isolated,ignore=shutil.ignore_patterns('__pycache__'))
            p=subprocess.run([sys.executable,str(isolated/'scripts/engine.py'),'validate','question_bank',str(isolated/'examples/aws-clf-c02-bank.private.json')],cwd=td,capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            # -S disables installed site packages to exercise the missing dependency branch.
            p=subprocess.run([sys.executable,'-S',str(isolated/'scripts/engine.py'),'validate','question_bank',str(isolated/'examples/aws-clf-c02-bank.private.json')],cwd=td,capture_output=True,text=True)
            self.assertEqual(p.returncode,2); self.assertIn('jsonschema ausente',p.stderr)


class EvidenceResult(unittest.TextTestResult):
    records=[]
    def addSuccess(self,test):
        super().addSuccess(test); self.records.append({'test':test.id(),'status':'PASS'})
    def addFailure(self,test,err):
        super().addFailure(test,err); self.records.append({'test':test.id(),'status':'FAIL','detail':self._exc_info_to_string(err,test)})
    def addError(self,test,err):
        super().addError(test,err); self.records.append({'test':test.id(),'status':'FAIL','detail':self._exc_info_to_string(err,test)})

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(Checks)
    result=unittest.TextTestRunner(verbosity=2,resultclass=EvidenceResult).run(suite)
    evidence={'scope':'Deterministic engine, contracts, CLI, isolated package; not model activation or host import',
              'python':sys.version,'jsonschema':version('jsonschema'),'PyYAML':version('PyYAML'),
              'skill_sha256':hashlib.sha256((SKILL/'SKILL.md').read_bytes()).hexdigest(),'tests':result.records,
              'run_count':result.testsRun,'success':result.wasSuccessful()}
    evidence_dir = ROOT / 'evidence'
    evidence_dir.mkdir(exist_ok=True)
    (evidence_dir / 'automated-results.json').write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )
    sys.exit(0 if result.wasSuccessful() else 1)
