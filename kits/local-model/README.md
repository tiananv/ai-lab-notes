# Local model on a laptop

**My question:** How do a laptop model and a hosted model compare on requirement quality and effort? I haven't recorded a comparison yet.

## What I need

The kit has a fictional workshop, a prompt and a blank checklist. I'll use [Ollama](https://docs.ollama.com/quickstart) with a downloaded model, plus a hosted chat app. Set `LOCAL_MODEL` and `HOSTED_MODEL` to their actual model names. Record the local model tag and digest from `ollama list`, app versions, laptop memory and operating system.

## Steps

1. Prepare the inputs and blank forms. Fill the run record's error and effort rule before starting.

```sh
uv run python -m scripts.prepare kit local-model --out runs/local-comparison
```

2. Download the chosen model with `ollama pull "$LOCAL_MODEL"`. With any existing Ollama server stopped, start it in another terminal using `OLLAMA_NO_CLOUD=1 ollama serve`. Keep using fictional material. Send the prepared prompt to the local model:

```sh
uv run python -m scripts.llm --backend ollama --model "$LOCAL_MODEL" --prompt runs/local-comparison/prompt.txt --out runs/local-comparison/local
```

3. Paste the same `runs/local-comparison/prompt.txt` into a fresh hosted chat. Save the full answer as `runs/local-comparison/hosted-answer.txt`, then keep a copy with its model details:

```sh
uv run python -m scripts.llm --backend manual --model "$HOSTED_MODEL" --prompt runs/local-comparison/prompt.txt --out runs/local-comparison/hosted --answer runs/local-comparison/hosted-answer.txt
```

Record setup, task, checking and correction time separately. Note whether the local model was already loaded. Keep failures and use a fresh folder for another attempt. The local helper requests a 32768-token context window; record an error if the laptop can't handle it.

## How I'll score it

For each row in `scoring.csv`, I'll give 0 for missing or wrong, 1 for partly correct, or 2 for fully supported by the workshop, with a quote from the answer. I'll compare row scores, totals and effort with the rule set before running. Hiding model names while scoring may help. This task only covers a small fictional workshop; running locally alone doesn't establish suitability for private material.
