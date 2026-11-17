# Usage examples

The tutor defaults to Brazilian Portuguese. These prompts explicitly request English. The bundled CLF-C02 question bank and templates are written in Brazilian Portuguese.

## Diagnostic and study plan

> I'm a beginner studying for AWS CLF-C02. I can study six hours a week and plan to take the exam in four weeks. Give me a short diagnostic, wait for my answers, and then build a study plan. Use English.

The tutor confirms the target date and exam guide, collects diagnostic answers, and uses them to build the plan. If key details such as the exam date or weekly time are missing, it asks for them. `student-profile.json` contains synthetic data. Use the learner's study preferences and keep personal identifiers out of the record.

## Guided Practice

> Run five English-language Guided Practice questions about IAM for CLF-C02. After each answer, explain the reasoning and any mistake I made.

The tutor checks the exam objective, creates and reviews the required items, and presents one question at a time. It records each answer and explains the right answer and distractors. The bundled bank has fewer than five IAM items, so the tutor generates additional questions for the session.

## Mock Exam

> Give me a 10-question AWS CLF-C02 mock exam in English at mixed difficulty. Show one question at a time and reveal the answer key only after I submit.

Answer with `B` or `B,D`. You can ask to skip a question, flag `CLF-P003`, or review `CLF-P002`. The bundled commands for those actions are `pular`, `marcar CLF-P003`, and `revisar CLF-P002`. Ask to submit explicitly, or use `finalizar`, to lock your choices and get the report. The synthetic demo scores 7/10 with its fixed test responses.

## Challenge an answer or resume a session

> I'd like to challenge the answer to CLF-P004. My reasoning is…

The tutor records the challenge, waits until submission during a mock exam, then checks the source and resolves the challenge or voids the item. Previous reports are retained.

> Resume my mock exam from the attached session records.

Resuming scoring requires the matching session state and frozen question bank. A public checkpoint preserves your responses and lets the tutor recover them even if the answer key is unavailable. Keep both records to resume scoring in a future conversation.

## Adaptive Practice

> Use my JSON reports to recommend what I should practice next. Explain the priorities in English.

The tutor validates the reports, groups attempts with compatible exam versions and practice modes, and schedules new practice around missed objectives. It flags small samples and uses an explicit rubric to estimate scores on open-ended answers. You can challenge those scores.
