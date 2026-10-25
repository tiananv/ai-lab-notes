# ai-lab-notes

- Six experiment kits for testing AI tools on business analysis tasks.
- Compare accuracy, consistency and time spent checking or correcting outputs.
- Use public or fictional inputs, with a scoring rule agreed before each experiment.

## Notes

<!-- NOTES:START -->

**First note coming soon.**

<!-- NOTES:END -->

## Validation results

- **22 software checks passed** using synthetic inputs. These are checker demonstrations, not completed AI experiments.
- **[Structured stories](tests/test_schema.py):** accepted the valid sample and rejected the sample with an invalid schema; meaning remains unscored.
- **[Spreadsheets](tests/test_excel.py):** accepted the requested sample edits with all six formulas preserved; rejected five damage scenarios and a missing sheet. Recalculated totals were not checked.
- **[Data dictionaries](tests/test_dictionary.py):** accepted a sample matching all nine schema columns; flagged missing, invented and duplicate columns. Description accuracy still needs human review.
- [Example datasets](tests/fixtures/README.md) · Reproduce: `uv run pytest -q tests/test_schema.py tests/test_excel.py tests/test_dictionary.py`.

## Experiment kits

- [Local models](kits/local-model/): workshop-note quality using a model running on a laptop.
- [CPS 230 context](kits/cps230-context/): answer accuracy against public APRA source documents.
- [Data dictionaries](kits/data-dictionary/): compare outputs and correction effort across tools.
- [User stories](kits/structured-stories/): consistency of structured outputs across repeated attempts.
- [Excel formulas](kits/excel-formulas/): check whether AI edits preserve spreadsheet formulas.
- [Voice memos](kits/voice-requirements/): transcription and requirements quality, including Australian accents.

## Published research — external results

- **Longer context did not guarantee reliable retrieval:** tested models often performed worse when relevant information appeared in the middle of a long input. [Liu et al., *Lost in the Middle*, 2024](https://aclanthology.org/2024.tacl-1.9/).
- Relevant to the context experiments above; completed results from these kits are still pending.

## Use

- Choose a kit, set the scoring rule, and keep the original outputs alongside correction time.
- [Running guide](docs/RUNNING.md), [note template](TEMPLATE.md) and [evidence checklist](evidence/README.md).

---

Built with help from AI coding tools. [MIT licence](LICENSE).
