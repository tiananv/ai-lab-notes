# Planned experiments

These are questions to investigate. All results are pending. Open a kit, decide the scoring rules, record a decision rule for acceptable errors and correction effort, and save a copy of its scoring sheet before starting.

| Kit | Question | Planned comparison |
| --- | --- | --- |
| [Local model](kits/local-model/) | How do a local and a hosted model compare on requirement quality and effort using fictional meeting material? | A downloaded Ollama model and a hosted model, both given the same fictional input |
| [CPS 230](kits/cps230-context/) | Does a model answer more accurately with a whole public standard or searched excerpts? | Same model and questions; whole document versus three pages picked by matching words in the question |
| [Data dictionary](kits/data-dictionary/) | Which agent needs less correction on a data dictionary job? | Copilot agent mode and Claude Code, using fresh copies of the same files |
| [Structured stories](kits/structured-stories/) | Can I get schema-valid JSON user stories every time? | Repeated fresh trials with a fixed prompt and schema |
| [Excel formulas](kits/excel-formulas/) | Can an agent update a workbook without breaking formulas? | Original workbook versus the actual edited workbook |
| [Voice requirements](kits/voice-requirements/) | How does transcription handle an Australian accent, and which errors change requirements? | Same self-recorded fictional script through chosen transcription tools |

Treat each comparison as evidence about that setup. A short task or a small sample cannot establish that a tool is always reliable. Keep failed attempts, distinguish setup time from task time, and record any corrections separately from the first response.
