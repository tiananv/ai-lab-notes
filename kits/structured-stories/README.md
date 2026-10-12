# Structured user stories

**My question:** How often does the answer match the required JSON format? I haven't collected responses yet. I'll also check whether the stories make sense.

## What I need

A chat tool, the fictional booking brief and the required fields in `inputs/schema.json`. Set `LLM_MODEL` to the model shown in the app. Read the [scoring guide](scoring.md) and choose the number of attempts before starting. The commands below use five.

## Steps

1. Copy the inputs and blank forms, then fill the run record's rule for acceptable errors and effort.

```sh
uv run python -m scripts.prepare kit structured-stories --out runs/stories
```

2. Prepare five copies of the same prompt:

```sh
uv run python -m scripts.run_trials --backend manual --model "$LLM_MODEL" --prompt runs/stories/prompt.txt --trials 5 --out runs/stories
```

3. For `trial-01` through `trial-05`, paste that folder's `prompt.txt` into a fresh chat and save the full answer as `answer.txt` there. Keep extra prose and Markdown fences. Import each answer, changing the trial name each time:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/stories/trial-01/prompt.txt --out runs/stories/trial-01 --answer runs/stories/trial-01/answer.txt
```

## How I'll score it

```sh
uv run python -m scripts.schema_score --runs runs/stories --expected 5 --output runs/stories/measured.csv
```

The script checks JSON syntax and required fields without repairing the answer. Missing responses leave the batch incomplete. Once all responses exist, the rate is valid responses divided by planned attempts. Use the same count in both commands if changing it before a run.

I'll copy `measured.csv` before filling its human scores, then use the rubric to check missing or invented requirements and testable acceptance criteria. A valid format doesn't establish a useful story. This kit checks prompt instructions; provider-specific format enforcement would be a separate comparison.
