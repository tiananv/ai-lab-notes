# CPS 230: long context or search

**My question:** Does the whole standard or a few searched pages help a model answer more accurately? I'll check answers against the source, without assessing a business's compliance. No answers are recorded yet.

## What I need

The kit's saved source details point to the July 2026 edition of [APRA CPS 230](https://www.apra.gov.au/standards/cps-230). The PDF stays local. Read APRA's [copyright terms](https://www.apra.gov.au/copyright) before sharing excerpts; the repository's MIT licence covers its original materials.

I'll use one model that accepts the whole document, with the same settings for both versions. Set `LLM_MODEL` to its actual identifier. Read [scoring.md](scoring.md) and check its reference points against the PDF before scoring.

## Steps

1. Copy the blank forms and download the recorded edition:

```sh
uv run python -m scripts.prepare kit cps230-context --out runs/cps230
uv run python -m scripts.cps230 download
```

2. Prepare both sets of prompts:

```sh
uv run python -m scripts.cps230 prepare --mode long-context --out runs/cps230/long-context-prompts
uv run python -m scripts.cps230 prepare --mode search --out runs/cps230/search-prompts
```

Long context uses every page. Search selects three pages by matching words in each question. Check the extracted text against the PDF and fill the run record's rule before starting. The download checks the file against the saved edition; a changed file needs review.

3. Shuffle and record the order of the ten prompts: `q1.txt` through `q5.txt` in each folder. Paste each into a fresh chat. Keep complete answers in separate files, including failures, and record elapsed time. Import each answer with the helper, for example:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/cps230/long-context-prompts/q1.txt --out runs/cps230/long-context/q1 --answer runs/cps230/q1-long-answer.txt
```

Use the matching prompt and fresh output folder for each answer. If the model rejects the whole document, keep that failure instead of shortening it.

## How I'll score it

I'll check each answer and citation against the original PDF using the rubric. Copy `prompt_characters` from each saved `.context.json` file into `scoring.csv`; it counts characters, not tokens. Keep missing answers visible. If search gives a wrong answer, inspect the selected pages to see whether the relevant text was available. This small document won't establish performance at a model's maximum context size.
