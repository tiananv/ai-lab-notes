# Local model on a laptop

**Question:** How do a local and a hosted model compare on requirement quality and effort using fictional meeting material? I haven't recorded a comparison yet. I'll use fictional material only; this task cannot establish that a configuration is suitable for private work.

## Inputs and setup

Give both models the same workshop file (`inputs/workshop.txt`) and prompt (`prompt.txt`), without editing either. The source is a made-up workshop at Fictional Paper Kookaburra Co. The checklist in `scoring.csv` is fixed before the run. Copy it and [the run record](../../docs/RUN_RECORD.md) to `runs/local-comparison/`. Before seeing answers, record a `decision_rule` for acceptable errors and checking and correction effort, and use the same rule for both models.

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

A hosted API can replace the chat app using the [optional command-line guide](../../docs/RUNNING.md#optional-run-it-from-the-command-line). Keep the actual prompt identical. Model-call metadata includes prompt hashes; compare them before scoring. Record cold-start versus warm-run timing, keep failures and use new folders for repeats. Both models receive only fictional material.

## Score before deciding

For each checklist row, score 0 for missing or wrong, 1 for partly correct, and 2 for fully supported by the input. Record a quotation or location from the actual answer as evidence. Add the criterion scores for each model and report the difference alongside the individual rows. Record elapsed time and setup effort separately. Hide the model labels during scoring if practical.

The same small task does not measure general model quality. Local execution alone does not establish privacy or fitness for sensitive work. Compare usefulness, errors and effort with the pre-run `decision_rule` when deciding the verdict. There is no completed score sheet or model output in this kit.
