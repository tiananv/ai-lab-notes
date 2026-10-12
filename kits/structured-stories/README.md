# Structured user stories

**Question:** Can a model return valid JSON user stories against a fixed schema on every planned trial? Results are pending. This kit tests instructions in the prompt; provider-specific schema enforcement is a separate experiment.

## Setup

Run `make setup`. Read `inputs/brief.txt`, `inputs/schema.json` and `scoring.md`. The brief describes a fictional booking service. Fix the model and trial count before starting. The command below prepares five identical trials in fresh directories. Set `LLM_MODEL` to the model displayed by your chosen chat tool. Copy [the run record](../../docs/RUN_RECORD.md) and `scoring.csv` into `runs/stories/`.

```sh
uv run python -m scripts.run_trials --backend manual --model "$LLM_MODEL" --prompt kits/structured-stories/prompt.txt --input kits/structured-stories/inputs/brief.txt --input kits/structured-stories/inputs/schema.json --trials 5 --out runs/stories
cp kits/structured-stories/scoring.csv docs/RUN_RECORD.md runs/stories/
```

## Run

For each of `trial-01` through `trial-05`, paste its `prompt.txt` into a fresh chat. Save the complete actual response as `answer.txt` in that trial directory. Include any Markdown fences or extra prose the model returns; stripping them would conceal a failure. Import each answer as follows, changing the trial name for each:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/stories/trial-01/prompt.txt --out runs/stories/trial-01 --answer runs/stories/trial-01/answer.txt
```

Alternatively, run the batch with a configured API backend and a fresh `--out` directory. That performs real calls. Retain failed attempts and evaluate retries as a separate batch. The [run guide](../../docs/RUNNING.md) explains model metadata and output limits.

## Check

```sh
uv run python -m scripts.schema_score --runs runs/stories --expected 5 --output runs/stories/measured.csv
```

The script fills JSON and schema validity columns and writes a summary beside the CSV. It evaluates every planned trial, rejects duplicate JSON keys and non-JSON numbers, and leaves `validity_rate` unset until all expected responses exist. A missing response is not a valid response. The final rate is valid responses divided by planned trials. It does not repair the model's answer.

Complete the human columns in a copy of `measured.csv`; rerunning the checker rewrites that file. Schema validity checks structure only. Use the rubric to check meaning and acceptance criteria. Even a completely valid batch cannot prove the model will succeed every time.
