# Empacotamento de plugins para ChatGPT e Codex

Referências oficiais consultadas em **17/11/2026**. Aplicar o contrato do importador de destino antes de gerar cada release.

| Formato | Manifesto | Local das Skills | Metadados de exibição |
|---|---|---|---|
| Agent Plugins, formato portátil recomendado para pacotes novos | `plugin.json` na raiz, com o `$schema` da versão do formato | Descoberta em `skills/<nome>/SKILL.md` | `extensions.com.openai.interface` |
| Compatibilidade Codex, usada na release 0.1.2 | `.codex-plugin/plugin.json` | `skills: "./skills/"` aponta para a pasta que contém cada Skill | `interface` na raiz do manifesto |

O pacote atual usa a segunda opção, a mesma estrutura encontrada no Cortex AI Skills e no Language Teacher. A tela **New Plugin** reconheceu o caminho do manifesto da versão 0.1.1 e acusou a ausência de `interface.longDescription`.

## Campos conferidos no formato de compatibilidade

| Campo | Validação aplicada neste projeto |
|---|---|
| `name`, `version`, `description` | Identificador técnico, versão de release e descrição preenchida |
| `author.name` | Nome de autor preenchido, com a mesma identificação usada no Language Teacher |
| `interface.displayName`, `shortDescription`, `longDescription`, `developerName` | Texto com conteúdo após remover espaços das extremidades. A descrição longa admite quebras de linha e tem limite de 4.000 caracteres. |
| `interface.category` e `capabilities` | Categoria reconhecida e lista de capacidades com limites documentados |
| `interface.logo`, `composerIcon` | Caminhos relativos para arquivos incluídos no ZIP. O projeto usa um PNG quadrado para os dois campos. |
| `interface.defaultPrompt` | Campo opcional. Até três sugestões em uma linha por item. |

Cada Skill fica na própria pasta com `name` e `description` no frontmatter YAML de `SKILL.md`. O empacotador inclui somente o manifesto, o ícone e os arquivos de uso da Skill.

## Verificar antes de distribuir

1. Conferir os campos obrigatórios e os limites da superfície. O nome de exibição atual tem mais de 30 caracteres. Ele cabe no limite de validação do pacote, e uma eventual submissão pública exigiria encurtá-lo.
2. Validar que cada caminho do manifesto existe dentro do ZIP. Os ícones devem ser quadrados e ter pelo menos 48 px. Para PNG, o limite superior documentado é 4096 px e 5 MiB.
3. Executar `python3 tests/test_plugin_package.py -v` e `python3 tools/package.py --plugin --version 0.1.2`. A checagem do empacotador cobre o manifesto e os ativos deste projeto.
4. Confirmar importação, instalação e seleção via `@` na interface autorizada. Registrar esse resultado separadamente da validação local.

O plugin contém apenas uma Skill. Os campos de servidores, aplicativos, credenciais e revisão de MCP se aplicam a pacotes com essas integrações.

- [Estrutura, compatibilidade e caminhos](https://developers.openai.com/plugins/build/plugins)
- [Campos de manifesto e requisitos de submissão](https://developers.openai.com/plugins/deploy/submission#manifest-fields)
- [Erros e limites de validação](https://developers.openai.com/plugins/deploy/submission-errors)
