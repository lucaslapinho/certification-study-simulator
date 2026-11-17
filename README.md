# Certification Teacher & Exam Simulator

Prepare for professional certifications with study plans, guided practice, mock exams, and targeted review based on your results.

**Plugin 0.1.2 · Skill 0.1.0**. The reproducible demo uses ten original practice questions for AWS CLF-C02. For other exams, specify the certification and provide the official exam guide if the session cannot access it.

## Install in ChatGPT

1. Download `certification-study-simulator-0.1.2-plugin.zip` from the [v0.1.2 release](https://github.com/lucaslapinho/certification-study-simulator/releases/tag/v0.1.2).
2. In ChatGPT, open **Plugins → Personal → Add → Upload plugin archive**. Upload the ZIP and click **Add plugin**. Click **Install** if prompted.
3. Start a new conversation, use `@` to select **Certification Teacher & Exam Simulator**, and ask for a mock exam.

Use the release asset for import. The ZIP under **Code → Download ZIP** contains the development repository.

> Use Certification Teacher & Exam Simulator for a 10-question AWS CLF-C02 mock exam. Run it in English, show one question at a time, and reveal the answer key when I ask to submit.

## Language

The tutor defaults to Brazilian Portuguese and is instructed to use the language you request for the session. To study in English, include “Run this session in English” in your first prompt. The plugin's listing descriptions, bundled demo questions, and static templates in v0.1.2 are written in Brazilian Portuguese.

## Study modes

| Mode | What to expect |
|---|---|
| Diagnostic and study plan | Identify the exam version, available study time, and priority topics. |
| Guided Practice | Get feedback and an explanation after each answer. |
| Mock Exam | Record and review your answers. See your score and explanations after submitting. |
| Adaptive Practice | Review missed objectives and practice new questions based on the records available. |

You can run the Skill through text commands. In a session with access to the source folder, ask the agent to read [SKILL.md](source/certification-study-simulator/SKILL.md) and its linked resources. Study records are portable in JSON, Markdown, and CSV.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r source/certification-study-simulator/scripts/requirements.txt 'PyYAML>=6,<7'
python tests/run_checks.py
python tests/test_plugin_package.py -v
python tools/demo.py
python tools/package.py --plugin --version 0.1.2
```

Use Python 3.10 or later. The tests cover data contracts, scoring, session transitions, exports, and archive metadata. The demo uses synthetic responses. The build writes the ZIP archives and `SHA256SUMS.txt` to `packages/0.1.2/`. Run `sha256sum -c SHA256SUMS.txt` in the directory with the downloaded files.

| Resource | Path |
|---|---|
| Skill, engine, contracts, and examples | [source/](source/certification-study-simulator/) |
| Manifest and icon | [plugin/](plugin/) |
| Tests and synthetic fixtures | [tests/](tests/) |
| Manifest and archive layout | [Packaging guide](docs/PLUGIN-PACKAGING.md) |
| Sample prompts | [Usage examples](docs/EXAMPLES.md) |
| Validation results and limits | [Validation](docs/VALIDATION.md) |
| Repository layout | [File index](docs/FILE-INDEX.md) |
| Release history | [Changelog](CHANGELOG.md) |

The plugin ZIP contains `.codex-plugin/plugin.json` and the Skill under `skills/certification-study-simulator/`. To test import and `@` selection, use a ChatGPT session with plugin support. Anyone with access to the demo question bank can inspect the answer key. Mock scores are diagnostic. Verify the exam's official sources before using the materials.
