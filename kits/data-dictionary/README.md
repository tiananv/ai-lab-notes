# Copilot agent mode and Claude Code

**My question:** Which agent leaves less for me to correct on a data dictionary? I haven't recorded either tool's output yet.

## What I need

A signed-in editor with Copilot agent mode and a signed-in Claude Code installation. Record versions, enabled tools and the model each displays. Set `COPILOT_MODEL` and `CLAUDE_MODEL` to those names. Both get the same fictional SQL and sample CSVs. The SQL defines the column rules; samples don't establish every allowed value.

## Steps

1. Prepare separate workspaces and blank forms. Read [scoring.md](scoring.md), choose the run order and fill the run record before starting.

```sh
uv run python -m scripts.prepare kit data-dictionary --out runs/dictionary
```

2. Open `runs/dictionary/copilot/workspace/` in the editor and start Claude Code from `runs/dictionary/claude/workspace/`. In fresh sessions, give both the full `runs/dictionary/prompt.txt`. Allow the same tools and changes only to each workspace's `dictionary.csv`.

3. Allow ten minutes per tool, stopping at its first completed file or the time limit. Keep that first CSV unchanged. Record time, interventions and failures. If no CSV comes back, record the failure. Save the real files with their model details:

```sh
uv run python -m scripts.llm --backend manual --model "$COPILOT_MODEL" --prompt runs/dictionary/prompt.txt --out runs/dictionary/copilot/record --answer runs/dictionary/copilot/workspace/dictionary.csv
uv run python -m scripts.llm --backend manual --model "$CLAUDE_MODEL" --prompt runs/dictionary/prompt.txt --out runs/dictionary/claude/record --answer runs/dictionary/claude/workspace/dictionary.csv
```

## How I'll score it

```sh
uv run python -m scripts.dictionary_score --candidate runs/dictionary/copilot/workspace/dictionary.csv --output runs/dictionary/copilot/measured.csv
uv run python -m scripts.dictionary_score --candidate runs/dictionary/claude/workspace/dictionary.csv --output runs/dictionary/claude/measured.csv
```

The checker compares coverage, types, nullability, duplicates and extra columns with the SQL. I'll copy each measured sheet before scoring descriptions with the rubric, then record correction time in `scoring.csv`. Invalid CSV counts as a failed task. A fast answer still needs useful descriptions; one small schema won't settle which agent is best overall.
