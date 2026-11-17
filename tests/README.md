# Avaliação

`run_checks.py`: 20 verificações executáveis de estrutura, motor e CLI. Usa fixtures sintéticos; não é avaliação de seleção de Skill pelo host. Dependências: Python 3.10+, jsonschema 4.x, PyYAML 6.x.

`prompts/cases.jsonl`: 20 cenários comportamentais. Entregar ao agente apenas o prompt, a fixture aplicável e a Skill. Não entregar `evaluator/`. Registrar saída, artefatos, hash da Skill, ambiente/modelo quando conhecido e escopo. O avaliador consulta `evaluator/rubrics.json` depois da execução.

`evaluator/expected.json` contém os valores independentes para o driver sintético. Testes de código e catálogo comportamental são camadas diferentes; um PASS no motor não aprova automaticamente o cenário do modelo.

Para regressão: executar os mesmos casos na versão anterior e na candidata; comparar contratos, resultados e falhas. Para esta primeira versão não há baseline anterior. Instalação e importação exigem autorização separada.
