# Uso do motor local

Python 3.10+ e jsonschema 4.18–4.x. Testes desta entrega usam versões registradas na evidência de desenvolvimento. O motor não consulta rede, não chama modelos, não instala nada e não agenda revisões. O tutor gera/revisa conteúdo e o motor valida/calcula. Se a dependência faltar, usar modo textual ou solicitar sua disponibilização conforme permissões do ambiente.

Executar a partir da pasta desta Skill; para outro diretório, substituir o caminho do script pelo absoluto real. Não presumir um caminho de instalação. Todos os exemplos criam arquivos novos em `work/`; se já existirem, usar nova revisão. Não sobrescrever.

```bash
python3 scripts/engine.py validate blueprint examples/aws-clf-c02-blueprint.json
python3 scripts/engine.py validate question_bank examples/aws-clf-c02-bank.private.json
python3 scripts/engine.py plan --profile examples/student-profile.json --blueprint examples/aws-clf-c02-blueprint.json --start-date 2026-11-16 --out work/plan.json
python3 scripts/engine.py start --bank examples/aws-clf-c02-bank.private.json --blueprint examples/aws-clf-c02-blueprint.json --mode mock --count 10 --out work/session-r0.json
```

O banco e as datas acima são exemplo sintético; usar os dados atuais do estudante. `exam_version: null` não significa versão desconhecida do código CLF-C02: significa ausência de um campo separado de versão do exame publicado. `blueprint_revision` fica separado.

O `start` imprime só a primeira projeção pública, não o banco. Para mostrar outra posição, aplicar goto. Não usar `cat` no banco em uma resposta ao aluno. Um banco novo pode ser gerado pelo tutor de acordo com o schema e revisto antes de `start`.

Criar um arquivo JSON de evento com a resposta efetivamente recebida (exemplo de forma, não gabarito):

```json
{
  "record_type": "event",
  "schema_version": "1.0",
  "event_id": "answer-001",
  "expected_revision": 0,
  "action": "answer",
  "payload": {"question_id": "CLF-P001", "answer": ["B"], "confidence": null},
  "at": null
}
```

`at` deve ser timestamp real com timezone, ou null; nunca fabricar o horário do aluno. `expected_revision` é a revisão lida. Para a mesma tentativa, gerar IDs de evento únicos. Reenvio idêntico não duplica resposta; em saída já existente, conferir estado antes de tentar de novo.

```bash
python3 scripts/engine.py apply --bank examples/aws-clf-c02-bank.private.json --session work/session-r0.json --event work/event.json --out work/session-r1.json
python3 scripts/engine.py view --bank examples/aws-clf-c02-bank.private.json --session work/session-r1.json
python3 scripts/engine.py checkpoint --bank examples/aws-clf-c02-bank.private.json --session work/session-r1.json --out work/checkpoint-r1.json
```

## Eventos

| action | payload exato |
|---|---|
| answer | question_id, answer (lista de IDs/texto/null), confidence (0–4/null) |
| goto / flag | question_id |
| next / submit / abandon | {} |
| challenge | question_id, reason |
| resolve | question_id, decision (`uphold` ou `void`), reason com fundamento/fonte |
| grade_open | question_id, grade (`evaluator`, `estimated: true`, `criteria`) |

Cada item de `grade.criteria` tem criterion_id, awarded e evidence. Todos os critérios devem constar. Não atribuir mais que o limite. Não usar `grade_open` antes da entrega de mock.

Depois de `submit`, com o caminho real da última revisão:

```bash
python3 scripts/engine.py report --bank examples/aws-clf-c02-bank.private.json --session work/session-final.json --outdir work/result-r1
python3 scripts/engine.py recommend --report work/result-r1/report.json --as-of 2026-11-16 --out work/recommendations.json
python3 scripts/engine.py compare work/history.json
```

Para guided/adaptive, chamar `feedback --bank ... --session ... --question-id ...` após a resposta. O motor bloqueia feedback antecipado no mock. `report` exige sessão submetida para todos os modos.

`start --history history.json` exclui IDs das duas últimas tentativas. `--difficulty basic|intermediate|advanced|mixed` filtra o banco. `--recommendations recommendations.json` é aceito com `--mode adaptive`. Se o banco não satisfizer contagem, domínio ou dificuldade, o motor falha explicitamente. Para escopo de domínios menor, criar um blueprint de sessão com só os domínios selecionados, pesos renormalizados e limitação de cobertura; preservar o blueprint oficial original.

## Saídas e falhas

`report.json` é o relatório canônico; `responses.csv` é a tabela de respostas/resultados; `report.md` inclui justificativas e fontes. Recomendações e plano possuem exports separados. Células CSV iniciadas por caracteres de fórmula são neutralizadas. Nunca tratar o CSV como banco de gabaritos.

Código de saída 0: operação concluída; 2: falha de contrato/entrada/arquivo. Erros de schema não imprimem o conteúdo privado. Se houver export parcial, listar arquivos presentes e usar diretório novo na recuperação; não alegar conclusão do conjunto inteiro. JSON schema e invariantes não detectam toda adulteração: sem assinatura, o histórico é um registro fornecido, não prova de autenticidade.
