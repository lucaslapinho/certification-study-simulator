#!/usr/bin/env python3
"""Reproducible synthetic 10-question flow; retains actual computed outputs."""
import importlib.util
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'source/certification-study-simulator'
spec=importlib.util.spec_from_file_location('engine',SKILL/'scripts/engine.py')
e=importlib.util.module_from_spec(spec); spec.loader.exec_module(e)

def main():
    dest=ROOT/'evidence/demo'
    if dest.exists(): raise SystemExit('Demo já existe: preserve a evidência ou use um checkout novo para reproduzir.')
    dest.mkdir(parents=True)
    bank=e.load(SKILL/'examples/aws-clf-c02-bank.private.json')
    bp=e.load(SKILL/'examples/aws-clf-c02-blueprint.json')
    profile=e.load(SKILL/'examples/student-profile.json')
    answers=e.load(ROOT/'tests/fixtures/answers.json')
    e.write_new(dest/'study-plan.json',e.plan(profile,bp,'2026-11-16'))
    s=e.start(bank,bp,session_id='synthetic-demo-001')
    # Use a stable illustrative timestamp explicitly labeled synthetic in the log.
    s['created_at']=None
    e.write_new(dest/'session-r0.json',s)
    log=[]
    for qid in s['question_ids']:
        log.append({'before_answer':e.view(s,bank),'student_answer':answers[qid]})
        ev=e.record('event',event_id='answer-'+qid,expected_revision=s['revision'],action='answer',payload={'question_id':qid,'answer':answers[qid],'confidence':None},at=None)
        s=e.apply_event(s,bank,ev)
        e.write_new(dest/f"session-r{s['revision']}.json",s)
    e.write_new(dest/'checkpoint-before-submit.json',e.checkpoint(s,bank))
    ev=e.record('event',event_id='submit',expected_revision=s['revision'],action='submit',payload={},at=None)
    s=e.apply_event(s,bank,ev)
    e.write_new(dest/'session-submitted.json',s)
    r=e.report(s,bank); e.export_report(r,dest/'result')
    e.write_new(dest/'recommendations.json',e.recommend(r,'2026-11-16'))
    e.write_new(dest/'history.json',e.record('attempt_history',student_id='learner-demo',attempts=[r]))
    e.write_new(dest/'transcript.json',{'nature':'Synthetic deterministic driver; not a real student or model conversation','turns':log,'submitted':True})
    print(json.dumps({'scope':'synthetic 10-item execution','status':'PASS','metrics':r['metrics']},ensure_ascii=False))

if __name__=='__main__': main()
