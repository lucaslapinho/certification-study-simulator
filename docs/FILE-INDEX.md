# Organização do repositório

| Caminho | Conteúdo |
|---|---|
| `source/certification-study-simulator/` | Fonte canônica da Skill, instruções, referências, schemas, motor, templates e exemplos |
| `plugin/.codex-plugin/plugin.json` | Manifesto e metadados de apresentação do plugin |
| `plugin/assets/` | Ícone utilizado na ficha do plugin e no seletor `@` |
| `tools/package.py` | Empacotador e validação de manifesto, caminhos e recursos |
| `tools/demo.py` | Execução sintética reproduzível de um simulado de dez questões |
| `tests/` | Testes, prompts e fixtures sintéticos |
| `docs/` | Decisões, instruções de empacotamento, exemplos de uso e validação |
| `evidence/` | Saídas locais geradas ao executar testes e a demonstração |
| `packages/` | Artefatos locais gerados pelo empacotador |

A release de plugin contém o manifesto em `.codex-plugin/`, o ícone em `assets/` e a Skill em `skills/certification-study-simulator/`. As cópias para desenvolvimento ficam no repositório.
