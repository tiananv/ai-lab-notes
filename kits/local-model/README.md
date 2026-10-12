# Local model on a laptop

**Question:** How much requirement quality is lost against a hosted model when the task would need to stay on a laptop? Results are pending. This experiment uses fictional material only; it cannot establish that a configuration is suitable for private work.

## Inputs and setup

Use `inputs/workshop.txt` and `prompt.txt` unchanged for both arms. The source is a made-up workshop at Fictional Paper Kookaburra Co. The checklist in `scoring.csv` is fixed before the run. Copy it and [the run record](../../docs/RUN_RECORD.md) to `runs/local-comparison/`.

Run `make setup`. Install [Ollama](https://docs.ollama.com/quickstart) separately, choose a downloaded local model that fits the laptop, and record its tag, digest from `ollama list`, Ollama version, laptop memory and operating system. Set `LOCAL_MODEL` to that model and `HOSTED_MODEL` to the exact model shown in a hosted chat app. Record the hosted app version if exposed, otherwise write unknown.

## Steps

Download the local model with `ollama pull "$LOCAL_MODEL"`. Quit any existing Ollama server, then start it in a separate terminal with `OLLAMA_NO_CLOUD=1 ollama serve`. This setting disables Ollama cloud features according to the [Ollama FAQ](https://docs.ollama.com/faq#how-do-i-disable-ollama-cloud-features). Keep using the fictional input even when running locally.

```sh
mkdir -p runs/local-comparison
cp kits/local-model/scoring.csv docs/RUN_RECORD.md runs/local-comparison/
uv run python -m scripts.llm --backend ollama --model "$LOCAL_MODEL" --prompt kits/local-model/prompt.txt --input kits/local-model/inputs/workshop.txt --out runs/local-comparison/local
uv run python -m scripts.llm --backend manual --model "$HOSTED_MODEL" --prompt kits/local-model/prompt.txt --input kits/local-model/inputs/workshop.txt --out runs/local-comparison/hosted
```

Paste the hosted `prompt.txt` into a fresh chat. Save the unedited answer as `runs/local-comparison/hosted/answer.txt`, then import it:

```sh
uv run python -m scripts.llm --backend manual --model "$HOSTED_MODEL" --prompt runs/local-comparison/hosted/prompt.txt --out runs/local-comparison/hosted --answer runs/local-comparison/hosted/answer.txt
```

A hosted API can replace the manual arm using the [shared backend guide](../../docs/RUNNING.md). Keep the actual prompt identical. Model-call metadata includes prompt hashes; compare them before scoring. Record cold-start versus warm-run timing, keep failures and use new folders for repeats. No private source material belongs in either arm.

## Score before deciding

For each checklist row, score 0 for missing or wrong, 1 for partly correct, and 2 for fully supported by the input. Record a quotation or location from the actual answer as evidence. Add the criterion scores for each arm and report the difference alongside the individual rows. Record elapsed time and setup effort separately. Blind the labels during scoring if practical.

The same small task does not measure general model quality. Local execution alone does not establish privacy or fitness for sensitive work. Decide the verdict from usefulness, errors and effort after the run. There is no completed score sheet or model output in this kit.
