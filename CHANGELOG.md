# Changelog

## Unreleased

- Translated the repository documentation and usage examples into English and documented the language settings for study sessions.

## Plugin 0.1.2 — 2026-11-17

- Added the required long description and completed the author, display, and capability fields.
- Added an original PNG icon used by `interface.logo` and `interface.composerIcon`.
- The packaging tool checks metadata and referenced files before building the ZIP.
- Added regression tests for the long description, developer identity, and icon paths.

## Plugin 0.1.1 — 2026-11-17

- Added an archive for **New Plugin**, with `.codex-plugin/plugin.json` and the Skill under `skills/certification-study-simulator/`.
- Added display metadata and three starter prompts to the manifest.
- Added regression tests for import paths and the integrity of packaged files.
- The Skill remained at version 0.1.0. The original 0.1.0 packages were preserved.

## 0.1.0 — 2026-11-16

First development implementation, before installation and publication.

- One Skill with Study Planner, AI Teacher, Exam Simulator, Performance Analyst, and Adaptive Learning Engine.
- Version 1.0 JSON contracts for questions, profiles, blueprints, plans, sessions, events, attempt history, reports, recommendations, and checkpoints.
- Engine with exact-match scoring, rubrics, answer revision, navigation, question challenges and invalidation, delayed feedback, and exports.
- CLF-C02 reference snapshot, ten original questions, an open-ended response example, and a synthetic learner profile.
- Twenty automated checks and a separate set of twenty behavioral and acceptance scenarios.
- Self-contained local resources and a distribution package that excludes evaluation keys and development evidence.

Development fixes deferred challenge analysis until mock exam submission (test12) and allowed sessions to select a subset of domains from a larger question bank (test04).

The project uses PATCH for compatible fixes and MINOR for new capabilities or contract changes in 0.x, with migration guidance where needed. The Skill and plugin have separate versions.
