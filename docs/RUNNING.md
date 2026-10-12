# Running an experiment

I'll start with a chat tool I'm allowed to use: paste a prompt, save the full answer, then check it. I haven't recorded a completed experiment yet. No script writes a note.

## Start with the manual workflow

1. Choose a [kit](../BACKLOG.md) and read its prompt, inputs and scoring guide. Copy [RUN_RECORD.md](RUN_RECORD.md) and the kit's blank scoring sheet into a fresh folder under `runs/`.
2. Record the model shown in the chat tool, the planned trial count and what would make the task useful. Set the acceptable errors and checking and correction effort before seeing an answer, as described below.
3. Follow the kit's preparation steps, then paste the full prompt and its inputs into a fresh chat in a tool you're allowed to use. Some kits prepare a workbook or document extracts first. Save the exact prompt sent, including the inputs, as `prompt.txt`. Keep it identical when comparing tools.
4. Save the complete answer as `answer.txt` in that trial's folder. Keep any JSON fences, extra prose, refusals or mistakes. Record the time spent and retain returned files such as a workbook or CSV as well. Save later corrections separately.
5. Run the kit's checks and fill its human scoring fields before writing a note. The [command-line helper](#optional-run-it-from-the-command-line) can prepare the prompt and import the saved answer with file fingerprints.

Keep raw material and outputs under ignored `runs/`; downloaded public data goes in ignored `data/raw/`. Only reviewed, shareable evidence goes into the tracked [evidence folder](../evidence/README.md).

## Before running

Record the actual tool versions, scoring criteria, planned trial count and `decision_rule` in the run record before seeing any answers. The rule must cover acceptable errors and the effort needed to check and correct the output. Define how you will measure time saved against doing the task yourself. Keep that rule unchanged when writing the verdict; if you revise it, record a new experiment rather than changing the earlier threshold.

## Saved evidence

Save the original prompt, answer, tool/model details and actual timings together for each trial. Record SHA-256 fingerprints, which identify the exact files being checked. A saved response might be incomplete, refuse the task or contain mistakes. I still need to check it.

The optional helper saves the exact UTF-8 `prompt.txt` and `metadata.json`. A completed trial also has `output.txt`. Metadata records backend, requested model, reported model ID where available, UTC timestamp, prompt and answer hashes, status and API/CLI elapsed seconds. Manual timing is blank because importing a file does not measure model response time. Record actual manual time in the run record. CLI and manual model IDs are user supplied; save the app's displayed model/version as supporting evidence.

The agent and voice kits also use interactive tools. Record their versions, actual model choices, full prompts, output files and timings in the same way. The kit instructions show how to retain text outputs with the manual backend. Transcription requires a real recording; the repository does not generate audio or claim to test accents automatically.

## From evidence to a note

Score first. A blank human score means no judgement has been made. Keep the original output alongside any corrected version. Compare the measured errors and effort with the pre-run `decision_rule`, and make any unmeasured threshold explicit. Summarise only what the evidence supports, including failed attempts.

### Publish the evidence

1. Review each proposed file, including prompts, outputs, metadata, run records and completed scoring sheets. Confirm that inputs are public or made up and that there is no employer or client material, personal information, credentials, private file paths or hidden document metadata. Check source terms and attribution before sharing public excerpts. If an original output cannot be shared safely, leave it in `runs/`, explain the evidence gap and limit the claim. Do not present an edited excerpt as the complete original.
2. Create `evidence/<note-slug>/`, where `<note-slug>` is the note filename without `.md`, including its date. Copy only the files that passed review: shareable original outputs, completed scoring sheets and the supporting prompts, metadata and run record where shareable. Keep each trial identifiable, include failed attempts and keep corrections in separate files. Never copy the whole raw run folder without reviewing its contents.
3. Add a `README.md` inside that evidence folder. Follow the [evidence checklist](../evidence/README.md): link each published file, map scores to original outputs, record the pre-run rule, input and output SHA-256 fingerprints, tool/model versions, source attribution and exact checking commands. Identify anything withheld or unmeasured. Hashes identify files; readers need the shareable originals to audit a score. Raw recordings and downloaded PDFs stay in their ignored folders.
4. Link the evidence folder's README where the note discusses its evidence, using `../evidence/YYYY-MM-DD-slug/README.md`. The template calls that section "What happened". Check every link and ensure the shareable evidence files are included with the note in the eventual authorised commit. `evidence/` is tracked; `runs/` remains ignored. Do not force-add raw material. Re-running a model is not guaranteed to reproduce the same words.

### Write the note

When you have a real result, copy `TEMPLATE.md` to `notes/YYYY-MM-DD-slug.md`, fill every field and write the note yourself. Copy the pre-run `decision_rule` into its required, non-empty, single-line field. Use `worth-it`, `maybe` or `not-yet` for `verdict`; `tools` and `tags` are non-empty YAML lists.

The template suggests starting with the question and verdict, then BA advice, setup and what happened. Adapt the headings and order to suit the note. The verdict must refer back to the decision rule and say which thresholds were met, missed or unmeasured. The index validates the dated filename and required front matter, including `decision_rule` and `verdict`; it does not check the body. I'll need to check that the note is complete, its evidence links work, the files are suitable to share and the verdict follows the rule. Run `make results` and `uv run pytest` before publishing.

## Setup and checks

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use the Python version in [.python-version](../.python-version). From the repository root, run:

```sh
make setup
make results
uv run pytest
```

These commands install the locked dependencies, rebuild the notes table and test the checking tools. They need no model account and produce no experiment results. `make index` also rebuilds the table. Run setup before using any of the kit's Python commands.

## Optional: run it from the command line

All scripted text calls use [scripts/llm.py](../scripts/llm.py). Supply `--backend` and `--model`, or set `LLM_BACKEND` and `LLM_MODEL`. Use the exact identifier of a model you can access.

### Import an answer from a chat tool

After setup, set `LLM_MODEL` to the exact model shown in the app. This command prepares a prompt without calling a model:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt kits/local-model/prompt.txt --input kits/local-model/inputs/workshop.txt --out runs/local-hosted
```

Open `runs/local-hosted/prompt.txt`, paste its full contents into a fresh chat and save the complete actual answer as `runs/local-hosted/answer.txt`. Repeat the same command with `--answer runs/local-hosted/answer.txt` appended. The helper imports it as `output.txt`, preserving the original answer.

For a prompt already saved in full, use that exact file as `--prompt` with no `--input` arguments. This also applies to prompts prepared by another script. You must keep the original backend, model and prompt when completing a pending trial. Completed outputs are never overwritten. Use another folder for a rerun and keep both attempts.

### Backend options

| Backend | Setup | Interface |
| --- | --- | --- |
| `manual` | Any chat app you're allowed to use; record the model displayed there | Writes `prompt.txt`, then imports the actual answer from `--answer` |
| `claude-cli` | Install Claude Code and sign in | Runs `claude -p` with tools and MCP disabled for a text-only trial |
| `anthropic` | Export `ANTHROPIC_API_KEY` locally | [Messages API](https://platform.claude.com/docs/en/api/messages/create) |
| `openai` | Export `OPENAI_API_KEY` locally | [Chat Completions API](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create) |
| `openrouter` | Export `OPENROUTER_API_KEY` locally | [Chat completion API](https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion) |
| `ollama` | Download a local model and start Ollama on this laptop | [Generate API](https://docs.ollama.com/api/generate) on `127.0.0.1:11434` |

Copy `.env.example` to `.env` if useful. It contains empty key fields. Nothing loads that file automatically; load your local values with `set -a; . ./.env; set +a`. Never paste credentials into a prompt or include them in a note. Missing keys return a short error.

Provider calls cap output at 4096 tokens; provider defaults otherwise apply. The local Ollama request also sets a 32768-token context window. Save hardware and memory details, and record errors if that setting exceeds the laptop's capacity. Settings and stop reasons, when returned, are recorded. Failed attempts are kept without automatic retries. See the [Claude CLI reference](https://code.claude.com/docs/en/cli-reference) for the text-only flags.
