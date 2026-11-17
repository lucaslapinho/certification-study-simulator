# Evaluation

- `run_checks.py` runs 20 structural, engine, and CLI checks with synthetic fixtures. Requirements are Python 3.10+, jsonschema 4.x, and PyYAML 6.x.
- `test_plugin_package.py` tests the manifest checks and archive contents.
- `prompts/cases.jsonl` contains 20 behavioral scenarios. Give the agent the prompt, relevant fixture, and Skill. Keep `evaluator/` with the evaluator. Record the output, artifacts, Skill hash, environment and model if known, and evaluation scope. Review `evaluator/rubrics.json` after execution.
- `evaluator/expected.json` contains independent expected values for the synthetic driver. Track host selection and model behavior separately from the automated engine checks.

For regression testing, run the same cases on the baseline and candidate and compare contracts, results, and failures. The initial version has no earlier baseline. Installation and import require separate authorization.
