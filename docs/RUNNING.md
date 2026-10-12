# Running an experiment

Every kit is pending until someone runs it. Keep raw material and outputs under ignored `runs/`; downloaded public data goes in ignored `data/raw/`. Only reviewed, shareable evidence goes into the tracked [evidence folder](../evidence/README.md). No script writes a note.

## Setup and checks

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use the Python version in [.python-version](../.python-version). From the repository root, run:

```sh
make setup
make results
uv run pytest
```

These commands install the locked dependencies, rebuild the index and test the harness. They need no model account and produce no experiment results. `make index` also rebuilds the index. To run an experiment, follow the steps in a [kit](../BACKLOG.md).

## Before running

Copy [RUN_RECORD.md](RUN_RECORD.md) and the kit's blank scoring sheet into a fresh folder under `runs/`. Record the actual tool versions, scoring criteria, planned trial count and `decision_rule` before seeing any answers. The rule must cover acceptable errors and the effort needed to check and correct the output. Define how you will measure time saved against doing the task yourself. Keep that rule unchanged when writing the verdict; if you revise it, record a new experiment rather than changing the earlier threshold.

## Model access

All scripted text calls use [scripts/llm.py](../scripts/llm.py). Supply `--backend` and `--model`, or set `LLM_BACKEND` and `LLM_MODEL`. Use an exact available model identifier. The repository deliberately does not choose a provider or guess which models an account can use.

| Backend | Setup | Interface |
| --- | --- | --- |
| `manual` | Any chat app; record the model displayed there | Writes `prompt.txt`, then imports the actual answer from `--answer` |
| `claude-cli` | Install Claude Code and sign in | Runs `claude -p` with tools and MCP disabled for a text-only trial |
| `anthropic` | Export `ANTHROPIC_API_KEY` locally | [Messages API](https://platform.claude.com/docs/en/api/messages/create) |
| `openai` | Export `OPENAI_API_KEY` locally | [Chat Completions API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) |
| `openrouter` | Export `OPENROUTER_API_KEY` locally | [Chat completion API](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion) |
| `ollama` | Download a local model and start Ollama on this laptop | [Generate API](https://docs.ollama.com/api/generate) on `127.0.0.1:11434` |

Copy `.env.example` to `.env` if useful. It contains empty key fields. Nothing loads that file automatically; load your local values with `set -a; . ./.env; set +a`. Never paste credentials into a prompt or include them in a note. Missing keys return a short error.

## Manual path

Set `LLM_MODEL` to the exact model shown in the app. A trial looks like this:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt kits/local-model/prompt.txt --input kits/local-model/inputs/workshop.txt --out runs/local-hosted
```

Open `runs/local-hosted/prompt.txt`, paste its full contents into a fresh chat and save the complete actual answer as `runs/local-hosted/answer.txt`. Do not clean up JSON, remove fences or improve wording. Repeat the same command with `--answer runs/local-hosted/answer.txt` appended. The harness imports it as `output.txt`. Keep human corrections in a separate file.

For a prompt already prepared by another script, use its `prompt.txt` as `--prompt` with no `--input` arguments. You must keep the original backend, model and prompt when completing a pending trial. Completed outputs are never overwritten. Use another folder for a rerun and keep both attempts.

## Saved evidence

Each trial directory contains the exact UTF-8 `prompt.txt` and `metadata.json`. A completed trial also has `output.txt`. Metadata records backend, requested model, reported model ID where available, UTC timestamp, prompt and answer hashes, status and API/CLI elapsed seconds. Manual timing is blank because importing a file does not measure model latency. Record actual manual time in the run record. CLI and manual model IDs are user supplied; save the app's displayed model/version as supporting evidence.

Provider calls cap output at 4096 tokens; provider defaults otherwise apply. The local Ollama request also sets a 32768-token context window. Save hardware and memory details, and record errors if that setting exceeds the laptop's capacity. Settings and stop reasons, when returned, are recorded. A completed transport response may still be truncated, refused or wrong: the checks and human score determine its usefulness. No automatic retry disguises a failed attempt. See the [Claude CLI reference](https://code.claude.com/docs/en/cli-reference) for the text-only flags.

The agent and voice kits include interactive steps outside this text harness. Record those tool versions, actual model choices, full prompts, output files and timings in the same way. The kit instructions show how to retain text outputs with the manual backend. Transcription requires a real recording; the repository does not generate audio or claim to test accents automatically.

## From evidence to a note

Score first. A blank human score means no judgement has been made. Keep the original output alongside any corrected version. Compare the measured errors and effort with the pre-run `decision_rule`, and make any unmeasured threshold explicit. Summarise only what the evidence supports, including failed attempts.

### Publish the evidence

1. Review each proposed file, including prompts, outputs, metadata, run records and completed scoring sheets. Confirm that inputs are public or made up and that there is no employer or client material, personal information, credentials, private file paths or hidden document metadata. Check source terms and attribution before sharing public excerpts. If an original output cannot be shared safely, leave it in `runs/`, explain the evidence gap and limit the claim. Do not present an edited excerpt as the complete original.
2. Create `evidence/<note-slug>/`, where `<note-slug>` is the note filename without `.md`, including its date. Copy only the files that passed review: shareable original outputs, completed scoring sheets and the supporting prompts, metadata and run record where shareable. Keep each trial identifiable, include failed attempts and keep corrections in separate files. Never copy the whole raw run folder without reviewing its contents.
3. Add a `README.md` inside that evidence folder. Follow the [evidence checklist](../evidence/README.md): link each published file, map scores to original outputs, record the pre-run rule, input and output SHA-256 fingerprints, tool/model versions, source attribution and exact checking commands. Identify anything withheld or unmeasured. Hashes identify files; readers need the shareable originals to audit a score. Raw recordings and downloaded PDFs stay in their ignored folders.
4. Link the evidence folder's README from the note's "What happened" section, using `../evidence/YYYY-MM-DD-slug/README.md`. Check every link and ensure the shareable evidence files are included with the note in the eventual authorised commit. `evidence/` is tracked; `runs/` remains ignored. Do not force-add raw material. Re-running a model is not guaranteed to reproduce the same words.

### Write the note

When you have a real result, copy `TEMPLATE.md` to `notes/YYYY-MM-DD-slug.md`, fill every field and write the note yourself. Copy the pre-run `decision_rule` into its required, non-empty, single-line field. Use `worth-it`, `maybe` or `not-yet` for `verdict`; `tools` and `tags` are non-empty YAML lists.

Keep the five main headings in this order: The question, Verdict, What I'd tell another BA, Setup, What happened. Use smaller headings (`###`) for extra detail. The verdict must refer back to the decision rule and say which thresholds were met, missed or unmeasured. The index checks the required metadata and section order; a person must check the evidence links, publication suitability and whether the verdict follows the rule. Run `make results` and `uv run pytest` before publishing.
