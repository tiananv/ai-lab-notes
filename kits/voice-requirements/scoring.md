# Predeclared scoring

Use one recording in both transcription tools. Preserve the raw outputs. Confirm the reference transcript against the recording yourself before using it for measurement. Record time spent correcting that reference separately from model task time.

The script calculates word error rate: the fewest word insertions, deletions and substitutions divided by reference words. It ignores case and punctuation only. Errors can exceed the number of reference words when many words are inserted, so the rate may exceed one. This metric is not a semantic quality score.

For `critical_terms_correct`, count how many of these six details survive accurately: four boards; Parramatta; half past four on Friday in Sydney time; approval above three boards; recording damage before closure; notification channel undecided. Accept equivalent number formatting for this human check even when the automatic word metric does not. Reconcile this checklist with what was actually spoken before running if the recording departs from the script.

For `requirements_correct`, count how many of these four rules are correct in the extracted requirements: closing time, approval threshold, damage before return closure, and draft without approval. Record any invented rule separately in the notes. Check the unresolved notification question as well.

Fill scores only after reading the actual transcript and requirements. Identify which stage introduced each error. Keep per-tool scores and observations rather than making a general accent claim from one speaker. The blank CSV is a scoring plan, not evidence of a completed run.
