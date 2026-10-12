# Predeclared rubric

Run five fresh trials with the same model and prompt. Keep the first complete response from each. Set a different trial count only before starting and use that same count in both commands.

Automated columns measure strict JSON parsing and conformance to the supplied JSON Schema. A missing trial leaves the batch incomplete. No syntax repair is allowed before scoring. A refusal or truncated response is still the actual response and may fail validation.

Score `semantic_score` as 0 when rules are invented or a key rule is wrong, 1 when the draft is mostly supported but has omissions or vague acceptance criteria, and 2 when the brief is covered accurately, criteria are testable, story IDs are unique, and the email question remains open. Record evidence in `reviewer_notes` and identify any human edits needed.

There is no automated claim that valid JSON is good business analysis. Report both structural and human scores, the planned and completed sample size, and any failed transport attempts. A small sample cannot establish an always-valid guarantee.
