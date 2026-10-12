# Update an Excel workbook

**My question:** Can an agent make the requested edits without breaking formulas or other cells? I still need a real edited workbook to check.

## What I need

An agent that can edit `.xlsx` files, plus Excel or LibreOffice for recalculation. Record their versions and set `LLM_MODEL` to the agent's displayed model. The order list is fictional, including its handling charge. Read the [scoring guide](scoring.md) before starting.

## Steps

1. Create a baseline workbook, a working copy and blank forms, then fill the run record.

```sh
uv run python -m scripts.prepare kit excel-formulas --out runs/excel
```

2. Open only `runs/excel/workspace/` in the agent, or upload its `candidate.xlsx`. Give it `runs/excel/prompt.txt`. Save the first returned workbook as `runs/excel/workspace/candidate.xlsx` and its final text reply as `runs/excel/answer.txt`. Keep the baseline outside the agent's workspace. If no workbook comes back, record a failed task.

3. Record task time and save the actual reply with model details:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/excel/prompt.txt --out runs/excel/record --answer runs/excel/answer.txt
```

## How I'll score it

```sh
uv run python -m scripts.excel check --baseline runs/excel/baseline.xlsx --candidate runs/excel/workspace/candidate.xlsx --output runs/excel/measured.csv
```

The script compares formulas, requested edits, other populated cells and sheet order. An unchanged workbook fails because the edits are missing. The CSV leaves the human checks blank; the JSON lists differences. Exit codes are 0 for a pass, 1 for a measured failure and 2 for unusable input.

I'll copy the measured sheet, then open a separate copy of the returned workbook in Excel or LibreOffice. Recalculate the subtotal from quantity times price, the charge as one tenth of the subtotal and the total as their sum. Check formatting too. The script reads formula text but doesn't calculate it. Keep corrections separate and record their time. This small workbook doesn't cover macros, pivots or external links.
