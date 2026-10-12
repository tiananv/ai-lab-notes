# Shareable experiment evidence

This tracked folder holds evidence from real experiments on public or made-up inputs. No experiment evidence has been published yet. Raw material stays in ignored `runs/`; downloaded source files stay in ignored `data/raw/`.

After a real run and publication review, create `evidence/<note-slug>/`. Use the note's complete filename without `.md`, including its date, for `<note-slug>`. Follow the [publishing steps](../docs/RUNNING.md#publish-the-evidence) before copying any files here.

Each note's evidence folder should contain shareable original outputs, completed scoring sheets and a `README.md` that lets a reader follow the scores. Include in that README:

- A link back to the note and the `decision_rule` recorded before running.
- Links to the original outputs and completed scoring sheets, with trial identifiers that connect each score to an output. Account for failures and missing trials.
- Supporting prompts, inputs or source links, run records and model metadata where shareable; record exact tool/model versions and input/output SHA-256 fingerprints.
- The exact checking commands, human scoring criteria, measured correction effort and any uncertainty. Keep corrected copies separate from original outputs.
- Source attribution, the publication review and any files or details withheld. State how missing evidence limits what a reader can check.

Link this per-note README from the note's "What happened" section. Only copy files after checking for employer/client material, personal information, credentials, private paths and hidden metadata. If an original is unsafe to share, keep it local and disclose the gap; do not label an edited excerpt as an original. Raw recordings and downloaded PDFs remain ignored. Test fixtures never belong here.
