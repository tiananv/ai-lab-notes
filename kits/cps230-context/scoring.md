# Decide the scoring before running

Use the original [July 2026 PDF](https://www.apra.gov.au/system/files/2026-05/Prudential%20Standard%20-%20CPS%20230%20Operational%20Risk%20Management%20-%20clean.pdf), with PDF page numbers starting at one. These reference points are a checking aid to verify before the experiment, not model outputs:

- q1: paragraph 32, page 7. Promptly, within 72 hours of awareness; retain the material-impact condition.
- q2: paragraph 37, page 8. Disruption duration, acceptable data loss, and minimum service during alternative arrangements.
- q3: paragraph 41, page 9. Promptly, within 24 hours; include disruption, actions, likely impact and restoration timeframe.
- q4: paragraph 42, page 9. All critical operations; an annual continuity exercise.
- q5: no organisation-specific recovery target is supplied. Paragraph 37 assigns tolerance-setting to the entity. An invented target fails.

For `correctness`, use 0 for wrong or unsupported, 1 for partly correct or missing a qualification, 2 for complete and supported. `citation_correct` is yes only when every cited paragraph and page supports its claim. Count substantive unsupported claims. Leave missing trials blank and label them missing in `reviewer_notes`. Reviewers must read the source themselves before scoring.

Report the per-question scores and the count of completed trials before any average. Record disagreements and how they were resolved. The sheet deliberately contains no scores. Verify the edition and reference points again if the PDF fingerprint changes. Do not infer that this is a comprehensive assessment of regulatory obligations.
