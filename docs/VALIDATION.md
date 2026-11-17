# Plugin 0.1.2 validation

| Area | Result | Reproduce |
|---|---|---|
| Skill and engine | PASS — 20 automated checks | `python tests/run_checks.py` |
| Manifest and packaged files | PASS — 4 automated checks | `python tests/test_plugin_package.py -v` |
| Reference mock exam | PASS — 10 questions, 7 correct with synthetic responses | `python tools/demo.py` |
| ZIP layout | PASS — Manifest and icon at the declared paths, with all 18 Skill files matching Skill 0.1.0 | `python tools/package.py --plugin --version 0.1.2` |

Packaging tests reject missing, empty, or whitespace-only `interface.longDescription` values. They also cover developer metadata and icon references that point outside the package or to missing files.

Engine checks cover scoring, withholding the answer key until submission, challenged items, recommendations, and exports. The tests and demo write their results to `evidence/`.

These results cover local checks. Upload, installation, and `@` selection depend on the ChatGPT interface and account. English-language conversation is requested at the prompt level and is outside the coverage of the automated suite. The AWS CLF-C02 demo bank is a dated sample of ten questions with partial exam coverage. Mock scores are diagnostic.
