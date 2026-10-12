# Running an experiment

I'll start with one kit and a chat tool I'm allowed to use. I haven't recorded a completed experiment yet. The preparation script copies inputs and blank forms; it doesn't supply answers or write a note.

## Before starting

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run commands from the repository folder. It uses `.python-version` and installs the packages in `uv.lock` automatically.

Choose a [kit](../BACKLOG.md) and follow its preparation command. This creates a fresh folder under `runs/` with `RUN_RECORD.md` and `scoring.csv`. Read the kit's scoring guide, then fill in the question, model, planned attempts and `decision_rule` before seeing any answers. That rule says how many errors are acceptable and how much checking and correction time would still make AI useful. Decide how to compare the time with doing the task yourself.

Commands containing `$LLM_MODEL` need that variable set to the model name shown in your tool. Other model variables work the same way. Record unknown if the tool hides its model, along with the tool name and version. Use the same inputs and prompt for both sides of a comparison.

## Save the actual answer

Paste the prepared prompt into a fresh chat. Keep the full first answer, including extra text, mistakes or refusals. Save it as `answer.txt` in that attempt's folder. Keep any returned workbook or CSV too. Record task time yourself; importing a file doesn't measure how long the model took.

For example, after preparing the user-stories trials, import the first saved answer:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/stories/trial-01/prompt.txt --out runs/stories/trial-01 --answer runs/stories/trial-01/answer.txt
```

The helper keeps `prompt.txt`, `output.txt` and `metadata.json` together. The metadata includes model details, time and file fingerprints that identify the exact prompt and answer. Use the original prompt and model when importing an answer. Completed outputs aren't overwritten, so a repeat needs a new folder.

Run the kit's checks on the original output. Copy `measured.csv` before adding human scores because running a checker again replaces that file. Keep corrections separate and count the effort they take. A blank score means unscored, not zero.

## Write a note

Copy the blank template to a local draft folder:

```sh
uv run python -m scripts.prepare note --out runs/first-note
```

After a real experiment, fill in `note.md` yourself. The suggested headings start with the question, verdict and advice for another BA. Explain which parts of the original `decision_rule` were met, missed or not measured.

Once the note and evidence are ready, copy it to `notes/YYYY-MM-DD-slug.md`. Match the header date to the filename, fill every header field and keep `decision_rule` on one line. The verdict is `worth-it`, `maybe` or `not-yet`; `tools` and `tags` are non-empty lists, and `time_spent` looks like `45 min` or `1 h`.

Update the README table:

```sh
uv run python -m scripts.build_index
```

The script checks the filename and header. I'll still need to read the note, check its evidence links and make sure the verdict follows the rule. An unfinished draft stays in `runs/`.

## Publish the evidence

I'll check each proposed file for employer or client material, personal details, credentials, private paths and hidden document metadata. Public excerpts need source attribution and permission under their source terms. Raw recordings and downloaded PDFs stay local.

Copy shareable original outputs and completed scoring sheets to `evidence/YYYY-MM-DD-slug/`, matching the note's name. Add a short README using the [evidence checklist](../evidence/README.md), then link it from the note. Include failed attempts and keep corrected copies separate. If an original can't be shared, leave it local and explain what a reader can't check. An edited excerpt isn't a complete original.

## Optional model connections

Manual mode works with a chat app. The same helper also accepts these `--backend` options:

| Option | What it needs |
| --- | --- |
| `claude-cli` | Claude Code installed and signed in; runs a text prompt with editing tools disabled |
| `anthropic` | `ANTHROPIC_API_KEY` |
| `openai` | `OPENAI_API_KEY` |
| `openrouter` | `OPENROUTER_API_KEY` |
| `ollama` | A downloaded model and Ollama running locally |

Use `--model` for the actual model identifier. Replacing manual mode with one of these options makes a real model call. Keep credentials local. `.env.example` lists the optional settings; `.env` isn't loaded automatically. Missing keys produce a short error. Interactive agent editing and audio transcription still happen in the tools described by those kits.
