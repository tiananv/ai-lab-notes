# Copilot agent mode and Claude Code

**Question:** Which agent needs less correction on the same data dictionary task? I haven't recorded either tool's output or correction time yet.

## Setup

Run `make setup`. Use a signed-in editor with [GitHub Copilot agent mode](https://code.visualstudio.com/docs/copilot/agents/overview) and a signed-in [Claude Code](https://code.claude.com/docs/en/overview) installation. Record editor, extension and CLI versions, the model each tool displays, and enabled tools. If a version or model is hidden, write unknown. Keep the agents' allowed actions comparable. This interactive experiment is separate from the shared backend's text-only `claude-cli` mode.

The SQL and CSV files under `inputs/` describe Fictional Paper Kookaburra Co. The SQL defines the structural facts; sample values do not establish business rules. Read `scoring.md` first. Set `COPILOT_MODEL` and `CLAUDE_MODEL` to the actual displayed model identifiers.

```sh
mkdir -p runs/dictionary/copilot/workspace runs/dictionary/claude/workspace
cp kits/data-dictionary/inputs/* runs/dictionary/copilot/workspace/
cp kits/data-dictionary/inputs/* runs/dictionary/claude/workspace/
cp kits/data-dictionary/scoring.csv docs/RUN_RECORD.md runs/dictionary/
uv run python -m scripts.llm --backend manual --model "$COPILOT_MODEL" --prompt kits/data-dictionary/prompt.txt --input kits/data-dictionary/inputs/schema.sql --input kits/data-dictionary/inputs/requests.csv --input kits/data-dictionary/inputs/services.csv --out runs/dictionary/copilot/record
uv run python -m scripts.llm --backend manual --model "$CLAUDE_MODEL" --prompt kits/data-dictionary/prompt.txt --input kits/data-dictionary/inputs/schema.sql --input kits/data-dictionary/inputs/requests.csv --input kits/data-dictionary/inputs/services.csv --out runs/dictionary/claude/record
```

## Run

Open the Copilot `workspace/` folder as the editor workspace, select Agent mode in chat, start a fresh conversation and paste the entire sibling `record/prompt.txt`. Start Claude Code from its own `workspace/` folder in a separate terminal, start a fresh conversation and paste its corresponding prompt. Only allow changes to `dictionary.csv` inside the respective workspace. No Git operations are part of the task.

Choose run order before starting. Use the same time limit of ten minutes per tool. Stop at the first completed file or the time limit. Record elapsed time, failures and any interventions. Do not manually fix the first output. If a tool does not produce a CSV, record the failure and leave that tool's output unscored rather than creating one yourself.

For each completed run, retain the actual CSV as a manual output. For example:

```sh
uv run python -m scripts.llm --backend manual --model "$COPILOT_MODEL" --prompt runs/dictionary/copilot/record/prompt.txt --out runs/dictionary/copilot/record --answer runs/dictionary/copilot/workspace/dictionary.csv
uv run python -m scripts.llm --backend manual --model "$CLAUDE_MODEL" --prompt runs/dictionary/claude/record/prompt.txt --out runs/dictionary/claude/record --answer runs/dictionary/claude/workspace/dictionary.csv
```

## Check

```sh
uv run python -m scripts.dictionary_score --candidate runs/dictionary/copilot/workspace/dictionary.csv --output runs/dictionary/copilot/measured.csv
uv run python -m scripts.dictionary_score --candidate runs/dictionary/claude/workspace/dictionary.csv --output runs/dictionary/claude/measured.csv
```

The checker builds the known schema in an in-memory SQLite database, then measures coverage, duplicate rows, extra columns, types and nullability. It does not ask a model to mark another model. Complete meaning scores in a copy of each measured sheet and record comparison-level time and correction effort in `scoring.csv`. Invalid CSV is a task failure, not permission to repair it before measurement.

A single small schema cannot establish which agent is best overall. Tool configuration, model, familiarity and order may affect the outcome. Keep the original files and any later corrections separately.
