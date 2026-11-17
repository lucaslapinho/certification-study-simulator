# Design decisions

- **One Skill for related study workflows.** Diagnosis, teaching, mock exams, and adaptive review share the exam version, session state, and learner records.
- **Verifiable scoring.** The Python engine validates records against a JSON Schema, manages session transitions, applies rubrics, and produces scores and reports. The tutor guides the session and reviews the content.
- **Portable records.** Plans, checkpoints, attempt history, and results can be saved to files. To resume a scored mock exam, retain the matching question bank and session revision.
- **Conversational interface.** Text commands let learners answer, flag, review, and submit questions across ChatGPT and Codex interfaces.
- **Original practice questions.** The demo bank covers a subset of AWS CLF-C02 objectives. Each item has official sources and a reviewed answer key. See the [source guide](../source/certification-study-simulator/references/certification-sources.md) and [question contract](../source/certification-study-simulator/references/question-contract.md) for adding exams and items.
- **Separate packaging.** Skill 0.1.0 contains the study workflows. Plugin 0.1.2 adds the distribution manifest and icon. See the [packaging guide](PLUGIN-PACKAGING.md) for the formats and fields.

See [Validation](VALIDATION.md) for the results of local checks and the checks that require a host application.
