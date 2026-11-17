# Certification Teacher & Exam Simulator

Plugin para estudar para certificações profissionais em português. Cria planos de estudo, conduz prática guiada e simulados, corrige respostas e indica quais temas revisar.

**Plugin 0.1.2 · Skill 0.1.0**. O exemplo reproduzível cobre dez questões originais para AWS CLF-C02. Para outros exames, informe a certificação e forneça o guia oficial quando a sessão não puder consultá-lo.

## Instalar no ChatGPT

1. Em **Releases**, baixe o asset `certification-study-simulator-0.1.2-plugin.zip`.
2. No ChatGPT, em **Plugins → Personal → Add → Upload plugin archive**, envie o ZIP e clique em **Add plugin**. Clique em **Install** se a interface oferecer essa etapa.
3. Em uma conversa nova, selecione **Certification Teacher & Exam Simulator** pelo `@` e peça um simulado.

O ZIP de código disponível em **Code → Download ZIP** tem a estrutura do repositório. Use o asset da release para importação.

> Use o Certification Teacher & Exam Simulator para um simulado AWS CLF-C02 de 10 questões. Apresente uma por vez e revele o gabarito quando eu disser finalizar.

## Como funciona

| Modo | O que acontece |
|---|---|
| Diagnóstico e plano | Identifica versão do exame, tempo disponível e temas prioritários. |
| Prática guiada | Corrige cada resposta e explica o raciocínio. |
| Simulado | Registra respostas, permite revisão e mostra a correção após `finalizar`. |
| Revisão adaptativa | Recomenda próximos exercícios com base nos erros e no histórico disponível. |

A Skill também funciona por texto. Em uma sessão com acesso à pasta, peça ao agente para ler o [SKILL.md](source/certification-study-simulator/SKILL.md) junto com os recursos locais. Os registros de estudo são portáteis em JSON, Markdown e CSV.

## Desenvolvimento

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r source/certification-study-simulator/scripts/requirements.txt 'PyYAML>=6,<7'
python tests/run_checks.py
python tests/test_plugin_package.py -v
python tools/demo.py
python tools/package.py --plugin --version 0.1.2
```

Use Python 3.10 ou mais recente. Os testes verificam os contratos, o cálculo de pontuação, as transições da sessão, a exportação e os metadados do ZIP. A demonstração usa respostas sintéticas. O build grava os ZIPs e `SHA256SUMS.txt` em `packages/0.1.2/`. Em um diretório novo, valide os downloads com `sha256sum -c SHA256SUMS.txt`.

| Recurso | Caminho |
|---|---|
| Skill, motor, contratos e exemplos | [source/](source/certification-study-simulator/) |
| Manifesto e ícone | [plugin/](plugin/) |
| Testes e fixtures sintéticos | [tests/](tests/) |
| Guia de manifesto e estrutura do ZIP | [docs/PLUGIN-PACKAGING.md](docs/PLUGIN-PACKAGING.md) |
| Prompts de exemplo | [docs/EXAMPLES.md](docs/EXAMPLES.md) |
| Evidências e limites | [docs/VALIDATION.md](docs/VALIDATION.md) |
| Organização do repositório | [docs/FILE-INDEX.md](docs/FILE-INDEX.md) |
| Histórico de mudanças | [CHANGELOG.md](CHANGELOG.md) |

O plugin usa `.codex-plugin/plugin.json`, com a Skill sob `skills/certification-study-simulator/` dentro do ZIP. Para testar importação e seleção pelo `@`, use uma sessão ChatGPT com suporte a plugins. O gabarito no banco de demonstração fica acessível a quem inspecionar os arquivos. A pontuação é diagnóstica e as fontes de cada exame devem ser verificadas antes do estudo.
