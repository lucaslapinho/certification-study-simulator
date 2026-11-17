#!/usr/bin/env python3
"""Local, explicit-state practice engine. No network calls or implicit persistence."""
from __future__ import annotations
import argparse
import copy
import csv
import hashlib
import io
import json
import re
import sys
import unicodedata
import uuid
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / 'schemas' / 'contracts.schema.json'
LIMIT = 8 * 1024 * 1024
VERSION = '0.1.0'


class ContractError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise ContractError(message)


def norm(value):
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, 'Chave JSON duplicada: ' + key)
        result[key] = value
    return result


def load(path):
    p = Path(path)
    require(p.stat().st_size <= LIMIT, 'Arquivo excede 8 MiB; divida o histórico.')
    return json.loads(p.read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda x: (_ for _ in ()).throw(ContractError('Número não finito')))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def write_new(path, value):
    """Exclusive create: immutable revisions, never overwrite an existing export."""
    p = Path(path)
    payload = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8') as f:
        f.write(payload)


def record(kind, **fields):
    return dict(record_type=kind, schema_version='1.0', **fields)


def identity(value):
    return {key: value[key] for key in ('certification_id', 'exam_code', 'exam_version')}


def validate(value, kind):
    try:
        from jsonschema import Draft202012Validator, FormatChecker
    except ImportError as exc:
        raise ContractError('Dependência jsonschema ausente. Use o fluxo textual ou disponibilize a dependência; não alegue validação.') from exc
    schema = load(SCHEMA_PATH)
    require(kind in schema['$defs'], 'Contrato desconhecido: ' + kind)
    selected = {'$schema': schema['$schema'], '$ref': '#/$defs/' + kind, '$defs': schema['$defs']}
    errors = list(Draft202012Validator(selected, format_checker=FormatChecker()).iter_errors(value))
    if errors:
        e = errors[0]
        # Do not echo the instance: it might contain a private answer key.
        raise ContractError('Contrato inválido em /' + '/'.join(map(str, e.absolute_path)) + ': regra ' + str(e.validator))
    if kind == 'question':
        ids = [o['id'] for o in value['options']]
        texts = [norm(o['text']) for o in value['options']]
        require(len(set(ids)) == len(ids), 'IDs de alternativas duplicados.')
        require(len(set(texts)) == len(texts) and all(texts), 'Alternativas vazias ou duplicadas.')
        require(bool(norm(value['stem'])), 'Enunciado vazio.')
        fmt, qt, key = value['response_format'], value['question_type'], value['correct_answers']
        require(qt == 'scenario-based' or {'single-choice':'single','multiple-response':'multiple','short-answer':'text'}[qt] == fmt,
                'Tipo e formato de resposta incompatíveis.')
        policy = value['scoring_policy']
        if fmt == 'text':
            require(not ids and not key and value['selection_count'] is None, 'Resposta aberta não usa alternativas/gabarito por IDs.')
            require(policy['method'] == 'rubric' and policy['rubric'], 'Resposta aberta exige rubrica.')
            rubric = policy['rubric']
            require(len({x['criterion_id'] for x in rubric}) == len(rubric), 'Critério duplicado.')
            require(sum(Decimal(str(x['points'])) for x in rubric) == Decimal(str(policy['max_points'])), 'Rubrica não soma o máximo.')
            require(not value['distractor_explanations'], 'Resposta aberta não tem distratores.')
        else:
            require(len(ids) >= 2 and key and set(key) <= set(ids), 'Gabarito ausente ou fora das alternativas.')
            require(value['selection_count'] == len(key), 'Quantidade declarada não confere com o gabarito.')
            require(len(key) == 1 if fmt == 'single' else 2 <= len(key) < len(ids), 'Quantidade de respostas corretas inválida.')
            require(policy['method'] == 'exact_match' and not policy['rubric'], 'Questões fechadas exigem correspondência exata.')
            require(set(value['distractor_explanations']) == set(ids) - set(key), 'Justificativas dos distratores incompletas.')
        if value['review_status'] == 'reviewed':
            require(value['reviewed_on'] is not None, 'Revisão exige data.')
            require(all(s['update_status'] == 'checked_snapshot' for s in value['source_references']), 'Fonte insuficiente para item revisado.')
    elif kind == 'question_bank':
        ids, stems = [], []
        for q in value['questions']:
            validate(q, 'question')
            ids.append(q['question_id']); stems.append(norm(q['stem']))
        require(len(set(ids)) == len(ids), 'Question ID duplicado.')
        require(len(set(stems)) == len(stems), 'Enunciado duplicado; criar novo cenário.')
    elif kind == 'blueprint':
        ids = [d['id'] for d in value['domains']]
        require(len(set(ids)) == len(ids), 'Domínio duplicado.')
        weights = [d['weight'] for d in value['domains']]
        require(all(w is None for w in weights) or all(w is not None for w in weights), 'Pesos parcialmente conhecidos; não completar por inferência.')
        if all(w is not None for w in weights):
            require(sum(Decimal(str(w)) for w in weights) == 100, 'Pesos oficiais não somam 100.')
        for d in value['domains']:
            require(len({o['id'] for o in d['objectives']}) == len(d['objectives']), 'Objetivo duplicado.')
    elif kind == 'study_plan':
        require(sum(w['available_minutes'] for w in value['weeks']) == value['total_minutes'], 'Total do plano inconsistente.')
        for w in value['weeks']:
            require(w['learn_minutes'] + w['practice_minutes'] + w['review_minutes'] == w['available_minutes'], 'Carga da semana inconsistente.')
            require(sum(a['minutes'] for a in w['by_domain']) == w['available_minutes'], 'Alocação dos domínios inconsistente.')
    return value


def allocation(total, weights):
    require(type(total) is int and total >= 0, 'Quantidade deve ser inteiro não negativo.')
    require(weights and all(Decimal(str(w)) >= 0 for w in weights.values()), 'Pesos inválidos.')
    denom = sum(Decimal(str(w)) for w in weights.values())
    require(denom > 0, 'Pesos zerados.')
    raw = {k: Decimal(total) * Decimal(str(w)) / denom for k, w in weights.items()}
    result = {k: int(v) for k, v in raw.items()}
    order = sorted(raw, key=lambda k: (-(raw[k] - result[k]), -Decimal(str(weights[k])), k))
    for k in order[:total-sum(result.values())]:
        result[k] += 1
    return result


def public_question(q):
    # Strict allowlist: no source titles, review notes, rubric solution or answer key.
    return {**{k: copy.deepcopy(q[k]) for k in ('question_id','stem','options','response_format','selection_count')},
            'public_criteria': q['scoring_policy']['public_criteria'], 'max_points': q['scoring_policy']['max_points']}


def checked_blueprint(bp):
    validate(bp, 'blueprint')
    require(bp['status'] == 'verified_snapshot', 'Blueprint indisponível, não verificado ou descontinuado; revalidar antes de pontuar.')
    require(all(s['update_status'] == 'checked_snapshot' for s in bp['sources']), 'Fontes do blueprint não verificadas.')


def start(bank, bp, mode='mock', count=10, difficulty='mixed', session_id=None, seen_ids=(), recommendations=None):
    validate(bank, 'question_bank'); checked_blueprint(bp)
    require(mode in ('guided','mock','adaptive'), 'Modo inválido.')
    require(difficulty in ('basic','intermediate','advanced','mixed'), 'Dificuldade inválida.')
    require(type(count) is int and count > 0, 'Quantidade deve ser positiva.')
    weights = {d['id']: d['weight'] if d['weight'] is not None else 1 for d in bp['domains']}
    limitations = list(bp['limitations'])
    if any(d['weight'] is None for d in bp['domains']):
        limitations.append('Distribuição pedagógica uniforme: pesos oficiais não publicados.')
    priority = set()
    if recommendations is not None:
        require(mode == 'adaptive', 'Recomendações somente em Adaptive Practice.')
        validate(recommendations, 'recommendations')
        require(identity(recommendations) == identity(bp), 'Recomendação de outro exame/versão.')
        priority = {p['objective'] for p in recommendations['priorities']}
        for p in recommendations['priorities']:
            require(p['domain'] in weights, 'Domínio da recomendação não existe.')
        for d in weights:
            if any(p['domain'] == d for p in recommendations['priorities']):
                weights[d] *= 2
        limitations.append('Alocação adaptativa pedagógica; não reproduz CAT oficial.')
    counts = allocation(count, weights)
    valid_objectives = {d['id']: {o['id'] for o in d['objectives']} for d in bp['domains']}
    buckets = {d: [] for d in weights}
    for q in bank['questions']:
        if identity(q) != identity(bp):
            continue
        if q['domain'] not in valid_objectives:
            continue  # A session blueprint may deliberately select only some domains.
        require(q['objective'] in valid_objectives[q['domain']], 'Questão não mapeada ao blueprint.')
        if q['review_status'] == 'reviewed' and q['question_id'] not in seen_ids and (difficulty == 'mixed' or q['difficulty'] == difficulty):
            buckets[q['domain']].append(q)
    for d in buckets:
        buckets[d].sort(key=lambda q: (q['objective'] not in priority, q['question_id']))
        require(len(buckets[d]) >= counts[d], 'Banco insuficiente em ' + d + '; gerar e revisar novos itens ou reduzir quantidade/escopo explicitamente.')
        buckets[d] = buckets[d][:counts[d]]
    ids = []
    while any(buckets.values()):
        for d in weights:
            if buckets[d]:
                ids.append(buckets[d].pop(0)['question_id'])
    s = record('exam_session', session_id=session_id or str(uuid.uuid4()), **identity(bp),
               blueprint_revision=bp['blueprint_revision'], bank_digest=digest(bank), mode=mode,
               status='in_progress', question_ids=ids, cursor=0, revision=0, difficulty=difficulty,
               responses={}, flagged=[], challenges={}, voided={}, resolutions={}, rubric_grades={},
               revealed_ids=[], events=[], policy_version='exact-match-v1',
               created_at=datetime.now(timezone.utc).isoformat(), submitted_at=None,
               distribution=counts, limitations=limitations)
    validate_session(s, bank)
    return s


def validate_answer(q, answer):
    if answer is None:
        return
    if q['response_format'] == 'text':
        require(isinstance(answer, str) and bool(answer.strip()), 'Resposta aberta exige texto não vazio.')
    else:
        require(isinstance(answer, list) and answer and all(isinstance(x, str) for x in answer), 'Use lista de IDs; null para pular.')
        require(len(set(answer)) == len(answer), 'Seleção duplicada.')
        require(set(answer) <= {o['id'] for o in q['options']}, 'Alternativa inexistente.')
        require(len(answer) == q['selection_count'], 'Selecione a quantidade indicada.')


def bank_map(bank):
    return {q['question_id']: q for q in bank['questions']}


def validate_session(s, bank):
    validate(s, 'session'); validate(bank, 'question_bank')
    require(s['bank_digest'] == digest(bank), 'Banco alterado ou perdido. Restaurar o banco congelado; não reconstruir o gabarito pelas respostas.')
    ids, bm = set(s['question_ids']), bank_map(bank)
    require(ids <= set(bm), 'Questão da sessão ausente no banco.')
    require(s['cursor'] < len(s['question_ids']), 'Cursor fora da sessão.')
    for field in ('responses','challenges','voided','resolutions','rubric_grades','flagged','revealed_ids'):
        require(set(s[field]) <= ids, 'Registro de questão fora da sessão: ' + field)
    for qid in ids:
        require(identity(bm[qid]) == identity(s), 'Mistura de certificação/versão.')
        require(bm[qid]['review_status'] == 'reviewed', 'Sessão usa questão sem revisão.')
    require(s['revision'] == len(s['events']), 'Revisão e log de eventos divergem.')
    require(len({e['event_id'] for e in s['events']}) == len(s['events']), 'Evento duplicado.')
    require(all(e['expected_revision'] == i for i,e in enumerate(s['events'])), 'Cadeia de revisões inválida.')
    for qid, response in s['responses'].items():
        validate_answer(bm[qid], response['answer'])
    require(Counter(bm[qid]['domain'] for qid in s['question_ids']) == Counter(s['distribution']), 'Distribuição inconsistente.')
    require(not (set(s['voided']) & set(s['challenges'])), 'Questão anulada ainda contestada.')
    for qid, g in s['rubric_grades'].items():
        validate_rubric(bm[qid], g, s['responses'].get(qid, {}).get('answer'))
    return s


def validate_rubric(q, grade, answer):
    validate(grade, 'rubric_grade')
    require(q['response_format'] == 'text' and isinstance(answer, str) and bool(answer.strip()), 'Só avaliar texto efetivamente respondido.')
    limits = {r['criterion_id']: Decimal(str(r['points'])) for r in q['scoring_policy']['rubric']}
    actual = [c['criterion_id'] for c in grade['criteria']]
    require(len(actual) == len(set(actual)) and set(actual) == set(limits), 'Critérios faltantes ou duplicados.')
    for c in grade['criteria']:
        require(Decimal(str(c['awarded'])) <= limits[c['criterion_id']], 'Pontos acima do máximo do critério.')


def apply_event(s, bank, event):
    validate_session(s, bank); validate(event, 'event')
    existing = next((e for e in s['events'] if e['event_id'] == event['event_id']), None)
    if existing:
        require(existing == event, 'Event ID reutilizado com conteúdo diferente.')
        return copy.deepcopy(s)
    require(event['expected_revision'] == s['revision'], 'Revisão antiga: releia o último checkpoint.')
    action, payload = event['action'], event['payload']
    fields = {
        'answer': {'question_id','answer','confidence'}, 'goto': {'question_id'}, 'next': set(),
        'flag': {'question_id'}, 'challenge': {'question_id','reason'},
        'resolve': {'question_id','decision','reason'}, 'grade_open': {'question_id','grade'},
        'submit': set(), 'abandon': set()}
    require(set(payload) == fields[action], 'Payload inválido para ' + action)
    require(s['status'] != 'abandoned', 'Sessão abandonada não pode ser retomada.')
    if s['status'] == 'submitted':
        require(action in ('challenge','resolve','grade_open'), 'Respostas congeladas após entrega.')
    qid = payload.get('question_id')
    if qid is not None:
        require(qid in s['question_ids'], 'Questão fora da sessão.')
    t = copy.deepcopy(s)
    bm = bank_map(bank)
    if action == 'answer':
        require(qid not in t['revealed_ids'], 'Resposta já corrigida; crie nova tentativa para praticar novamente.')
        validate_answer(bm[qid], payload['answer'])
        c = payload['confidence']
        require(c is None or type(c) is int and 0 <= c <= 4, 'Confiança deve ser 0–4 ou null.')
        t['responses'][qid] = {'answer':payload['answer'], 'confidence':c, 'recorded_at':event['at']}
        t['cursor'] = min(t['question_ids'].index(qid)+1, len(t['question_ids'])-1)
        if t['mode'] != 'mock' and payload['answer'] is not None:
            t['revealed_ids'].append(qid)
    elif action == 'goto':
        t['cursor'] = t['question_ids'].index(qid)
    elif action == 'next':
        t['cursor'] = min(t['cursor']+1, len(t['question_ids'])-1)
    elif action == 'flag':
        if qid in t['flagged']: t['flagged'].remove(qid)
        else: t['flagged'].append(qid)
    elif action == 'challenge':
        require(isinstance(payload['reason'], str) and bool(payload['reason'].strip()), 'Explique a contestação.')
        require(qid not in t['voided'], 'Questão já anulada.')
        t['challenges'][qid] = payload['reason']
    elif action == 'resolve':
        require(t['mode'] != 'mock' or t['status'] == 'submitted', 'Analisar contestação após a entrega do mock.')
        require(qid in t['challenges'], 'Não há contestação pendente.')
        require(payload['decision'] in ('uphold','void'), 'Decisão deve manter ou anular; não mudar gabarito congelado.')
        require(isinstance(payload['reason'], str) and bool(payload['reason'].strip()), 'Resolução exige fundamento e fonte.')
        t['resolutions'][qid] = payload['reason']
        del t['challenges'][qid]
        if payload['decision'] == 'void':
            t['voided'][qid] = payload['reason']
    elif action == 'grade_open':
        require(t['status'] == 'submitted' or t['mode'] != 'mock', 'Não corrigir resposta aberta antes da entrega do mock.')
        validate_rubric(bm[qid], payload['grade'], t['responses'].get(qid,{}).get('answer'))
        t['rubric_grades'][qid] = payload['grade']
    elif action == 'submit':
        t['status'] = 'submitted'; t['submitted_at'] = event['at']
    elif action == 'abandon':
        t['status'] = 'abandoned'
    t['events'].append(copy.deepcopy(event)); t['revision'] += 1
    validate_session(t, bank)
    return t


def view(s, bank):
    validate_session(s, bank)
    qid = s['question_ids'][s['cursor']]
    return {'session_id':s['session_id'], 'status':s['status'], 'revision':s['revision'],
            'position':s['cursor']+1, 'total':len(s['question_ids']),
            'answered':sum(r['answer'] is not None for r in s['responses'].values()),
            'question':public_question(bank_map(bank)[qid]),
            'responses':copy.deepcopy(s['responses']), 'flagged':list(s['flagged'])}


def checkpoint(s, bank):
    validate_session(s, bank)
    return validate(record('student_checkpoint', session=copy.deepcopy(s),
                          questions=[public_question(bank_map(bank)[i]) for i in s['question_ids']],
                          resume_requires=['Banco congelado com SHA-256 correspondente, mantido separadamente.',
                                           'Sem o banco, preservar respostas e reiniciar avaliação; não inferir gabarito.']), 'checkpoint')


def score_item(q, s):
    qid = q['question_id']; answer = s['responses'].get(qid,{}).get('answer')
    maximum = Decimal(str(q['scoring_policy']['max_points']))
    earned, possible = Decimal(0), maximum
    reason, grade, estimated = None, s['rubric_grades'].get(qid), q['response_format'] == 'text'
    if qid in s['voided'] or qid in s['challenges']:
        outcome, possible = 'excluded', Decimal(0)
        reason = s['voided'].get(qid) or 'Contestação pendente: ' + s['challenges'][qid]
    elif answer is None:
        outcome = 'unanswered'
    elif q['response_format'] == 'text':
        if grade is None:
            outcome, possible, reason = 'pending', Decimal(0), 'Aguardando avaliação estimativa por critérios.'
        else:
            validate_rubric(q, grade, answer)
            earned = sum(Decimal(str(c['awarded'])) for c in grade['criteria'])
            outcome = 'correct' if earned == maximum else 'partial' if earned > 0 else 'incorrect'
    else:
        earned = maximum if set(answer) == set(q['correct_answers']) else Decimal(0)
        outcome = 'correct' if earned == maximum else 'incorrect'
    return dict(question_id=qid,domain=q['domain'],subdomain=q['subdomain'],objective=q['objective'],
                difficulty=q['difficulty'],answer=answer,correct_answers=q['correct_answers'],
                outcome=outcome,earned=float(earned),possible=float(possible),estimated=estimated,
                explanation=q['explanation'],distractor_explanations=q['distractor_explanations'],
                source_references=q['source_references'],reason=reason,rubric_evaluation=grade)


def metrics(items):
    counts = Counter(x['outcome'] for x in items)
    earned = sum(Decimal(str(x['earned'])) for x in items)
    possible = sum(Decimal(str(x['possible'])) for x in items)
    return dict(valid=sum(counts[x] for x in ('correct','incorrect','partial','unanswered')),
                **{x:counts[x] for x in ('correct','incorrect','partial','unanswered','excluded','pending')},
                earned=float(earned),possible=float(possible),
                percentage=float((earned*100/possible).quantize(Decimal('0.01'))) if possible else None)


def feedback(s, bank, qid):
    validate_session(s, bank)
    require(qid in s['question_ids'], 'Questão fora da sessão.')
    require(s['status'] == 'submitted' or s['mode'] != 'mock' and qid in s['revealed_ids'], 'Gabarito oculto até a entrega/resposta.')
    return score_item(bank_map(bank)[qid], s)


def report(s, bank):
    validate_session(s, bank)
    require(s['status'] == 'submitted', 'Finalize a sessão antes do relatório e gabarito.')
    items = [score_item(bank_map(bank)[qid],s) for qid in s['question_ids']]
    domains, subdomains = defaultdict(list), defaultdict(list)
    for item in items:
        domains[item['domain']].append(item)
        subdomains[item['domain']+' / '+item['subdomain']].append(item)
    r = record('performance_report',session_id=s['session_id'],session_revision=s['revision'],**identity(s),
               blueprint_revision=s['blueprint_revision'],bank_digest=s['bank_digest'],mode=s['mode'],policy_version=s['policy_version'],
               provisional=bool(s['challenges']) or any(i['outcome']=='pending' for i in items),
               metrics=metrics(items),by_domain={d:metrics(v) for d,v in domains.items()},
               by_subdomain={d:metrics(v) for d,v in subdomains.items()},items=items,
               limitations=s['limitations']+['Pontuação de prática, sem equivalência ao score oficial ou previsão de aprovação.',
                                           'Amostras pequenas não demonstram domínio; respostas abertas são estimativas.'])
    return validate(r,'report')


def verify_report(r):
    validate(r, 'report')
    require(r['metrics'] == metrics(r['items']), 'Totais adulterados ou incorretos.')
    require(len({i['question_id'] for i in r['items']}) == len(r['items']), 'Itens duplicados no relatório.')
    for field, key in [('by_domain',lambda i:i['domain']),('by_subdomain',lambda i:i['domain']+' / '+i['subdomain'])]:
        grouped = defaultdict(list)
        for item in r['items']: grouped[key(item)].append(item)
        require(r[field] == {k:metrics(v) for k,v in grouped.items()}, 'Agregação divergente: ' + field)
    return r


def recommend(r, as_of):
    verify_report(r)
    day = date.fromisoformat(as_of)
    priorities = []
    groups = defaultdict(list)
    for item in r['items']:
        if item['outcome'] in ('incorrect','partial','unanswered'):
            groups[(item['domain'],item['objective'])].append(item)
    for (domain, objective), items in groups.items():
        m = r['by_domain'][domain]
        # Small samples only support a provisional practice priority, not a mastery claim.
        next_diff = 'basic' if m['valid'] >= 5 and (m['percentage'] or 0) < 50 else 'unchanged'
        priorities.append(dict(domain=domain,objective=objective,question_ids=[i['question_id'] for i in items],
                               evidence=f"{len(items)} item(ns) com erro, crédito parcial ou sem resposta; domínio com n={m['valid']}.",
                               next_action='Rever a justificativa e fonte; explicar o conceito sem consulta; resolver um cenário novo do objetivo.',
                               next_difficulty=next_diff,review_dates=[(day+timedelta(days=d)).isoformat() for d in (1,3,7,14)]))
    priorities.sort(key=lambda p:(-len(p['question_ids']),p['domain'],p['objective']))
    return validate(record('adaptive_recommendations',session_id=r['session_id'],**identity(r),as_of=as_of,
                           priorities=priorities,interleaving='Alternar objetivos frágeis com outro domínio; preferir questões inéditas.',
                           limitations=['Intervalos 1/3/7/14 dias são heurística ajustável; não são lembretes agendados.',
                                        'Não elevar dificuldade com uma única tentativa ou com n<5; exigir desempenho repetido em itens novos.',
                                        'Itens contestados e pendentes não indicam lacuna do estudante.']), 'recommendations')


def plan(profile, bp, start_date, diagnostic=None):
    validate(profile,'student_profile'); checked_blueprint(bp)
    require(identity(profile) == identity(bp), 'Perfil e blueprint divergem.')
    begin, target = date.fromisoformat(start_date), date.fromisoformat(profile['target_date'])
    require(target > begin, 'Data de exame deve ser posterior ao início do plano.')
    require((target-begin).days <= 730, 'Horizonte acima de dois anos: dividir o plano.')
    known = {d['id'] for d in bp['domains']}
    require(set(profile['self_confidence']) <= known, 'Autoconfiança usa domínio desconhecido.')
    if diagnostic:
        verify_report(diagnostic)
        require(identity(diagnostic)==identity(bp), 'Diagnóstico de outro exame/versão.')
    weights = {}
    for d in bp['domains']:
        weight = Decimal(str(d['weight'] if d['weight'] is not None else 1))
        observed = diagnostic['by_domain'].get(d['id']) if diagnostic else None
        if observed and observed['valid'] > 0:
            deficit = 1 - Decimal(str(observed['percentage'] or 0))/100
        else:
            deficit = 1 - Decimal(profile['self_confidence'].get(d['id'],2))/4
        weights[d['id']] = weight*(1+deficit)
    weeks=[]; cursor=begin
    while cursor < target:
        end=min(cursor+timedelta(days=7),target)
        available=profile['weekly_minutes']*(end-cursor).days//7
        learn=available*60//100; practice=available*25//100
        weeks.append(dict(start=cursor.isoformat(),end=(end-timedelta(days=1)).isoformat(),available_minutes=available,
                          learn_minutes=learn,practice_minutes=practice,review_minutes=available-learn-practice,
                          by_domain=[{'domain':d,'minutes':m} for d,m in allocation(available,weights).items()]))
        cursor=end
    total=sum(w['available_minutes'] for w in weeks)
    require(total > 0, 'Tempo insuficiente; ajustar data ou disponibilidade.')
    return validate(record('study_plan',student_id=profile['student_id'],**identity(profile),
                           blueprint_revision=bp['blueprint_revision'],start_date=start_date,target_date=profile['target_date'],
                           weekly_minutes=profile['weekly_minutes'],total_minutes=total,
                           allocation_basis='peso × (1 + lacuna observada ou autodeclarada); 60% estudo, 25% prática, restante revisão',
                           weeks=weeks,review_offsets_days=[1,3,7,14],
                           assumptions=['Disponibilidade distribuída igualmente pelos dias; adaptar aos dias livres informados.',
                                        'Autoconfiança não equivale a diagnóstico. Associar objetivos e atividades a cada bloco.',
                                        'Não incluir o dia do exame; revisões posteriores requerem extensão explícita.',
                                        'Cronograma pedagógico; não garante cobertura integral nem aprovação.']+bp['limitations']), 'study_plan')


def compare_history(history):
    validate(history,'history')
    seen=set(); groups=defaultdict(list)
    for r in history['attempts']:
        verify_report(r)
        require(r['session_id'] not in seen, 'Uma tentativa por session_id; escolher revisão mais recente explicitamente.')
        seen.add(r['session_id'])
        key=(r['certification_id'],r['exam_code'],r['exam_version'],r['blueprint_revision'],r['mode'],r['policy_version'])
        groups[key].append(r)
    out=[]
    for key, reports in groups.items():
        repeated=len({i['question_id'] for r in reports for i in r['items']}) < sum(len(r['items']) for r in reports)
        out.append({'group':list(key),'attempts':[{'session_id':r['session_id'],'percentage':r['metrics']['percentage'],'provisional':r['provisional']} for r in reports],
                    'repeated_items':repeated,'limitation':'Comparação descritiva; bancos e dificuldades podem diferir. Não inferir ganho psicométrico.'})
    return out


def csv_safe(value):
    text=str(value)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text


def export_report(r, destination):
    verify_report(r)
    dest=Path(destination)
    require(not dest.exists(), 'Diretório de exportação já existe; usar revisão nova.')
    dest.mkdir(parents=True)
    write_new(dest/'report.json',r)
    stream=io.StringIO(); writer=csv.writer(stream)
    writer.writerow(['question_id','domain','subdomain','objective','outcome','earned','possible','answer','estimated'])
    for item in r['items']:
        writer.writerow([csv_safe(json.dumps(item[k],ensure_ascii=False) if k=='answer' else item[k]) for k in ('question_id','domain','subdomain','objective','outcome','earned','possible','answer','estimated')])
    write_new(dest/'responses.csv',stream.getvalue())
    def safe(x): return str(x).replace('|','\\|').replace('\n',' ')
    m=r['metrics']; pct='N/A' if m['percentage'] is None else str(m['percentage'])+'%'
    lines=[f"# Relatório — {safe(r['exam_code'])}",'',f"Resultado de prática: {m['earned']}/{m['possible']} ({pct}).",
           f"Corretas: {m['correct']}; incorretas: {m['incorrect']}; parciais: {m['partial']}; sem resposta: {m['unanswered']}; excluídas: {m['excluded']}; pendentes: {m['pending']}.",
           f"Provisório: {'sim' if r['provisional'] else 'não'}.",'','| Domínio | Pontos | Percentual | n válido |','|---|---:|---:|---:|']
    for domain,v in r['by_domain'].items():
        lines.append(f"| {safe(domain)} | {v['earned']}/{v['possible']} | {v['percentage'] if v['percentage'] is not None else 'N/A'} | {v['valid']} |")
    for item in r['items']:
        lines += ['',f"## {safe(item['question_id'])} — {item['outcome']}",f"Resposta: {safe(item['answer'])}; gabarito: {safe(item['correct_answers'])}.",item['explanation']]
        lines += [f"- {safe(k)}: {v}" for k,v in item['distractor_explanations'].items()]
        lines += [f"- Fonte: {s['url']} (consulta {s['accessed_on']})." for s in item['source_references']]
        if item['reason']: lines.append(item['reason'])
    lines += ['','## Limites',''] + ['- '+s for s in r['limitations']]
    write_new(dest/'report.md','\n'.join(lines)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    v=sub.add_parser('validate'); v.add_argument('kind'); v.add_argument('input')
    st=sub.add_parser('start')
    for key in ('bank','blueprint','out'): st.add_argument('--'+key,required=True)
    st.add_argument('--mode',default='mock',choices=['guided','mock','adaptive'])
    st.add_argument('--count',type=int,default=10); st.add_argument('--difficulty',default='mixed')
    st.add_argument('--session-id'); st.add_argument('--history'); st.add_argument('--recommendations')
    for command in ('apply','view','feedback','report','checkpoint'):
        p=sub.add_parser(command)
        p.add_argument('--bank',required=True); p.add_argument('--session',required=True)
        if command=='apply': p.add_argument('--event',required=True); p.add_argument('--out',required=True)
        if command=='feedback': p.add_argument('--question-id',required=True)
        if command=='report': p.add_argument('--outdir',required=True)
        if command=='checkpoint': p.add_argument('--out',required=True)
    p=sub.add_parser('plan')
    for key in ('profile','blueprint','start-date','out'): p.add_argument('--'+key,required=True)
    p.add_argument('--diagnostic')
    p=sub.add_parser('recommend')
    for key in ('report','as-of','out'): p.add_argument('--'+key,required=True)
    p=sub.add_parser('compare'); p.add_argument('history')
    a=parser.parse_args()
    if a.command=='validate': validate(load(a.input),a.kind); result={'status':'PASS','scope':'schema_and_semantic_checks','kind':a.kind}
    elif a.command=='start':
        seen=[]
        if a.history:
            history=load(a.history); compare_history(history)
            seen=[i['question_id'] for r in history['attempts'][-2:] for i in r['items']]
        s=start(load(a.bank),load(a.blueprint),a.mode,a.count,a.difficulty,a.session_id,seen,load(a.recommendations) if a.recommendations else None)
        write_new(a.out,s); result=view(s,load(a.bank))
    elif a.command in ('apply','view','feedback','report','checkpoint'):
        s,bank=load(a.session),load(a.bank)
        if a.command=='apply':
            s=apply_event(s,bank,load(a.event)); write_new(a.out,s); result=view(s,bank)
        elif a.command=='view': result=view(s,bank)
        elif a.command=='feedback': result=feedback(s,bank,a.question_id)
        elif a.command=='report':
            r=report(s,bank); export_report(r,a.outdir); result={'status':'PASS','files':['report.json','report.md','responses.csv'],'metrics':r['metrics']}
        else: write_new(a.out,checkpoint(s,bank)); result={'status':'PASS','contains_answer_key':False}
    elif a.command=='plan':
        write_new(a.out,plan(load(a.profile),load(a.blueprint),a.start_date,load(a.diagnostic) if a.diagnostic else None)); result={'status':'PASS'}
    elif a.command=='recommend':
        write_new(a.out,recommend(load(a.report),a.as_of)); result={'status':'PASS'}
    else: result=compare_history(load(a.history))
    print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))


if __name__=='__main__':
    try: main()
    except (ContractError,ValueError,KeyError,TypeError,OSError) as exc:
        print('ERRO: '+str(exc),file=sys.stderr); sys.exit(2)
