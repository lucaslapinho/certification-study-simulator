# Decisões de projeto

- **Uma Skill para quatro fluxos de estudo.** Diagnóstico, ensino, simulados e revisão adaptativa compartilham a versão do exame, o estado da sessão e os registros do estudante.
- **Cálculo verificável.** O motor em Python valida JSON Schema, controla as transições da sessão, aplica rubricas e gera pontuação e relatórios. O tutor conduz a experiência e revisa o conteúdo.
- **Registros portáteis.** Planos, checkpoints, histórico e resultados podem ser preservados em arquivos. Para retomar um simulado, conserve o banco e a revisão correspondentes.
- **Interface conversacional.** Os comandos textuais permitem responder, marcar, revisar e finalizar em superfícies distintas do ChatGPT e do Codex.
- **Questões originais.** O banco de demonstração usa um recorte de AWS CLF-C02 com fontes oficiais e gabarito revisto. Os capítulos de [fontes](../source/certification-study-simulator/references/certification-sources.md) e [contrato de questões](../source/certification-study-simulator/references/question-contract.md) orientam extensões.
- **Empacotamento separado.** A Skill 0.1.0 mantém a lógica de estudo. O plugin 0.1.2 adiciona o manifesto e o ícone para a distribuição. A [referência de empacotamento](PLUGIN-PACKAGING.md) descreve os formatos e campos usados.

A [validação](VALIDATION.md) distingue os resultados locais das verificações que dependem do host.
