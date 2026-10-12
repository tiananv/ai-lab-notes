# CPS 230: long context or search

**Question:** Does a model answer more accurately with a whole public standard or with searched excerpts? I'll check answers against the standard, without assessing a business's compliance. I haven't recorded any answers yet.

## Source and setup

Run `make setup`. The kit targets the July 2026 edition of [APRA CPS 230](https://www.apra.gov.au/standards/cps-230), published with the [April 2026 amendments](https://www.apra.gov.au/consultations/operational-risk-management). The exact source URL and fingerprint are in `inputs/source.json`. The PDF is downloaded locally, never included in the publishable tree. APRA's [copyright terms](https://www.apra.gov.au/copyright) specify CC BY 4.0 with exceptions for logos, the Coat of Arms and third-party material. The MIT licence covers this kit's code and original materials. See APRA's terms for its requested attribution before sharing excerpts.

Read `scoring.md` before running. The questions in `inputs/questions.csv` stay fixed. Choose one model with enough context for the full document and set `LLM_MODEL` to its exact identifier. Use the same model and settings for the full document and the searched excerpts. Copy the blank scoring sheet and run record.

## Prepare the comparison

```sh
make cps230
mkdir -p runs/cps230
cp kits/cps230-context/scoring.csv docs/RUN_RECORD.md runs/cps230/
uv run python -m scripts.cps230 prepare --mode long-context --out runs/cps230/long-context-prompts
uv run python -m scripts.cps230 prepare --mode search --out runs/cps230/search-prompts
```

Download once, then reuse `data/raw/cps230/`. The preparation command validates the PDF hash and saves a context manifest beside each prompt. Review text extraction against the PDF before starting. Long context includes every PDF page. Search uses three pages picked by matching words in the question. The selection details are in [the code](../../scripts/cps230.py).

## Run and score

The following prepares manual trials without calling a model:

```sh
for mode in long-context search; do
  for question in q1 q2 q3 q4 q5; do
    uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt "runs/cps230/$mode-prompts/$question.txt" --out "runs/cps230/$mode/$question"
  done
done
```

Randomise the order in which you present the prepared prompts and record that order. Use a fresh chat for each answer. Save each actual answer in its trial folder as `answer.txt`, then import it with the same command plus `--answer`. For example:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/cps230/long-context/q1/prompt.txt --out runs/cps230/long-context/q1 --answer runs/cps230/long-context/q1/answer.txt
```

To use an API, replace `--backend manual` in the loop with a configured backend from the [run guide](../../docs/RUNNING.md). This makes real model calls. Score all answers against the original PDF and `scoring.md`, not against another model. Copy `prompt_characters` from each context manifest into the sheet and record elapsed time. Character counts are not token counts.

Keep failures and unsupported answers. If the model rejects a context, record it rather than silently shortening the document. This standard fits many modern context windows, so the kit does not by itself test performance at their maximum size. A search failure may reflect retrieval, answer generation, or both. Inspect the saved pages to distinguish them.
