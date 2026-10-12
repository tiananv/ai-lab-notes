# Running an experiment

Run commands from the repository root after `make setup`. Every kit is pending until someone runs it. Keep raw material and outputs under ignored `runs/`; downloaded public data goes in ignored `data/raw/`. Copy [RUN_RECORD.md](RUN_RECORD.md) into each experiment folder and record the actual tool versions. No script writes a note.

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

Score first. A blank human score means no judgement has been made. Keep the original output alongside any corrected version. Summarise only what the evidence supports, including failed attempts. When you have a real result, copy `TEMPLATE.md` to `notes/YYYY-MM-DD-slug.md`, fill every field and write the note yourself. Use `worth-it`, `maybe` or `not-yet` for `verdict`; `tools` and `tags` are non-empty YAML lists. Run `make results` and `uv run pytest`.

Before publishing, select only evidence you can share publicly. Raw run folders remain ignored. If you publish excerpts in a note, record the input and output hashes, tool/model versions and exact scoring command so another person can follow the result. Re-running a model is not guaranteed to reproduce the same words.
