# Experiment record template

Copy this file into a fresh folder under `runs/`. Fill the question, scoring criteria, planned trial count and `decision_rule` before running. Complete the other fields during the real run.

The `decision_rule` says what would make the task worth doing with AI, including acceptable errors and correction effort. For example: "worth it if at most 2 of 10 answers need major correction and it saves at least 15 minutes". This is an example threshold, not a result. Define major correction and the time comparison before seeing answers; include checking and correction time. Keep the original rule and compare the verdict with it, even if the result disappoints.

- Question and kit:
- UTC date and time:
- Tools and exact versions:
- Backend and requested model ID:
- Model ID actually reported, or how it was shown in the app:
- Input files and SHA-256 fingerprints:
- Prompt file and SHA-256 fingerprint:
- Source edition and source file hash, if applicable:
- Hardware, operating system and memory, if relevant:
- Tool settings, extensions and enabled capabilities:
- Fixed scoring criteria and planned trial count:
- decision_rule:
- Run order and fresh-session procedure:
- Setup time:
- Task time:
- Provider-reported cost, or unknown:
- Actual response/output paths:
- Failures, interruptions and corrections:
- Checking commands and score sheet paths:
- Human scoring, evidence and remaining uncertainty:
- Verdict against decision_rule, including unmet or unmeasured thresholds:
- Publication review and shareable evidence paths:

This is a record form, not an experiment result. An empty field means unrecorded, not zero.
