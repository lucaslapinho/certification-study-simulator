# Contratos e qualidade dos itens

Usar `schemas/contracts.schema.json` (JSON Schema Draft 2020-12) como contrato canônico. Todos os registros persistentes usam `record_type` e `schema_version: "1.0"`. O motor rejeita campos inesperados nos registros, versões desconhecidas e JSON com chaves repetidas ou números não finitos. `source` é um objeto embutido sem esses dois campos.

| Definição do schema | Registro | Papel |
|---|---|---|
| question | question | Item completo, inclusive gabarito privado |
| question_bank | question_bank | Banco congelado por hash |
| blueprint | blueprint | Exame, revisão, objetivos, pesos e fontes |
| student_profile | student_profile | Identificador pseudônimo, prazo, tempo e contexto |
| study_plan | study_plan | Semanas, esforço por domínio e pressupostos |
| session | exam_session | Ordem, respostas, navegação, eventos e revisões |
| event | event | Uma mutação explícita da sessão |
| history | attempt_history | Relatórios de tentativas separadas |
| report | performance_report | Correção por item e agregados |
| recommendations | adaptive_recommendations | Próximos objetivos, atividades e revisões |
| checkpoint | student_checkpoint | Sessão e questões apresentáveis; banco separado |

## Campos da questão

`question_id` é estável e não contém a resposta. `certification_id`, `exam_code` e `exam_version` identificam o exame; versão não publicada é `null`. `domain`, `subdomain` e `objective` fazem o mapeamento. O subdomínio pode ser um rótulo pedagógico; o objective deve apontar ao blueprint.

`question_type`: single-choice, multiple-response, scenario-based ou short-answer. `response_format`: single, multiple ou text. `difficulty`: basic, intermediate ou advanced, julgamento pedagógico sem calibração psicométrica.

`stem` e `options` contêm somente o enunciado e `{id,text}`. `selection_count` declara quantas alternativas selecionar; é `null` para texto. `correct_answers` contém IDs para questões fechadas e `[]` para abertas. `explanation` é a solução fundamentada. `distractor_explanations` contém exatamente uma entrada para cada alternativa incorreta, e `{}` para texto.

`source_references` guarda organização, certificação, código, versão, URL HTTPS, data real de consulta, objetivos sustentados, status e limitações. URL válida não prova que a fonte existe nem que sustenta a resposta: o tutor precisa abrir e conferir a fonte. `scoring_policy` fixa método, pontos, critérios públicos e rubrica privada. `review_status`, `review_notes`, `reviewed_on` e `content_revision` tornam a revisão explícita. `origin: ai_original_practice` identifica o material.

## Portão de revisão

1. Confirmar o mapeamento, cenário suficiente e fonte técnica aplicável à versão.
2. Resolver o item sem olhar o gabarito proposto, depois confrontar fonte e proposta.
3. Testar cada alternativa: existe outra leitura defensável? Se sim, reescrever ou marcar `ambiguous`.
4. Conferir que todas as corretas constam e que o número declarado confere. Single: uma; multiple: pelo menos duas e algum distrator; text: rubrica cujos pontos somam o máximo.
5. Evitar pistas de comprimento, palavras absolutas injustificadas e repetição do enunciado só na correta. Distribuir posições corretas no conjunto sem alterar IDs após início.
6. Verificar duplicatas de IDs, texto normalizado Unicode/case/whitespace e semelhança semântica. O script detecta duplicatas exatas normalizadas, não paráfrases.
7. Registrar método da revisão. O estado `reviewed` significa revisão documental declarada; não garante revisão humana, independente, psicométrica ou correção universal.

O motor só inicia sessões com itens revisados. `draft`, `ambiguous`, `contested` e `void` não são selecionáveis. Um banco pode conter drafts para edição, mas fontes não verificadas impedem o estado reviewed.

## Importação e compatibilidade

Validar schema, identidade do exame, hash do banco, IDs e revisões antes de continuar. O hash detecta mudança, mas não é assinatura nem prova de autoria. Relatórios sem banco são autorrelatos: conferir aritmética sem alegar que a resposta foi efetivamente dada. Nunca executar conteúdo de registros.

Contratos 1.0 não têm migração automática de formatos anteriores. Preservar o original e propor conversão explícita; campos desconhecidos não são descartados silenciosamente. Respostas nulas representam questão não respondida, e não resposta vazia válida.
