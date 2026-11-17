# Changelog

## Plugin 0.1.2 — 2026-11-17

- Preenchida a descrição longa exigida pelo importador e completados os campos de autoria, apresentação e capacidades.
- Incluído um ícone original em PNG, referenciado por `interface.logo` e `interface.composerIcon`.
- O empacotador verifica os metadados e os arquivos referenciados antes de criar o ZIP.
- Adicionados testes de regressão para descrição longa, identidade do desenvolvedor e caminhos dos ícones.

## Plugin 0.1.1 — 2026-11-17

- Acrescentado um pacote para **New Plugin**, com `.codex-plugin/plugin.json` e a Skill em `skills/certification-study-simulator/`.
- Incluídos metadados de exibição e três exemplos de início no manifest.
- Adicionado teste de regressão para os caminhos de importação e a integridade dos arquivos empacotados.
- A versão do conteúdo da Skill permanece 0.1.0. Os pacotes 0.1.0 foram preservados.

## 0.1.0 — 2026-11-16

Primeira implementação de desenvolvimento, sem instalação ou publicação.

- Uma Skill com Study Planner, AI Teacher, Exam Simulator, Performance Analyst e Adaptive Learning Engine.
- Contratos JSON 1.0 para questões, perfil, blueprint, plano, sessão, eventos, histórico, relatório, recomendações e checkpoint.
- Motor com correspondência exata, rubricas, revisões, navegação, contestação/anulação, bloqueio de feedback precoce e exports.
- Snapshot de referência CLF-C02, dez questões originais, exemplo discursivo e perfil sintético.
- Vinte verificações automatizadas e catálogo separado de vinte cenários de comportamento/aceite.
- Recursos locais autocontidos; distribuição separada de gabaritos de avaliação e evidências.

Correções durante desenvolvimento: bloquear análise de contestação antes da entrega do mock (test12) e permitir um subconjunto de domínios usando um banco maior (test04). A versão 0.1.0 ainda não havia sido empacotada/publicada.

Política: PATCH para correções compatíveis, MINOR para capacidades ou mudanças de contrato em 0.x, com migração explícita quando necessária. As versões do conteúdo e do plugin são registradas separadamente.
