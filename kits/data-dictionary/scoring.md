# Predeclared scoring

Both tools receive the same instructions and files in fresh sessions. Allow ten minutes per arm. Record task time and any interventions. Score the first produced file, including failures, before asking for corrections.

The automated check measures coverage of every SQL column, declared data types, nullability, duplicate entries and invented columns. A non-empty description is only a presence check. A structural pass does not mean the descriptions are accurate.

For each row's `meaning_score`, use 0 for incorrect or invented meaning, 1 for plausible but incomplete meaning or unstated uncertainty, and 2 for a useful description supported by the schema or samples, with assumptions clearly labelled. Check specifically that the model does not infer all allowed values from samples, claim that requested_on has an enforced date format, or invent a rule linking status to closure_reason. Those constraints are absent from the SQL.

In the comparison sheet, count rows requiring a human correction and record the actual time to correct a separate copy. Preserve both versions. Compare coverage, errors and effort together; do not choose a winner from speed alone.
