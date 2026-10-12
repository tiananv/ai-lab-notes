# Update an Excel workbook

**Question:** Can an agent change the requested cells without breaking formulas or unrelated content? Results are pending.

## Setup and input

Run `make setup`. `inputs/orders.csv` is a made-up order list for Fictional Paper Kookaburra Co. `scripts/excel.py` creates the workbook from it. The handling charge is a fictional arithmetic rule, not a tax rule. Choose an agent capable of reading and writing `.xlsx` files. Record its version, model and file-editing capabilities. Set `LLM_MODEL` to the actual model shown.

Read `scoring.md` before running, then prepare a baseline and a working copy:

```sh
make excel
mkdir -p runs/excel/workspace
cp runs/excel/baseline.xlsx runs/excel/workspace/candidate.xlsx
cp kits/excel-formulas/scoring.csv docs/RUN_RECORD.md runs/excel/
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt kits/excel-formulas/prompt.txt --out runs/excel/record
```

The baseline stays outside the agent's workspace. `make excel` refuses to overwrite it. To repeat the experiment, use `scripts.excel create --output` with a fresh directory and copy that new baseline.

## Run

Open only `runs/excel/workspace/` in the agent's editing environment, or upload `candidate.xlsx` to a tool that supports workbook editing. Give it the full `runs/excel/record/prompt.txt`. Save the returned workbook as `runs/excel/workspace/candidate.xlsx`. Save the actual final text response as `runs/excel/record/answer.txt` and import it:

```sh
uv run python -m scripts.llm --backend manual --model "$LLM_MODEL" --prompt runs/excel/record/prompt.txt --out runs/excel/record --answer runs/excel/record/answer.txt
```

Record upload/download actions, elapsed time, tool versions and model choice. The text record describes the interaction; the workbook is the evidence being checked. Keep the original candidate before applying any manual correction. If no workbook comes back, record a failed task.

## Check

```sh
uv run python -m scripts.excel check --baseline runs/excel/baseline.xlsx --candidate runs/excel/workspace/candidate.xlsx --output runs/excel/measured.csv
```

Exit code 0 means the automatic checks pass, 1 means a measured failure, and 2 means unusable input. The CSV contains measurable scores and blank human checks. The accompanying JSON records both workbook hashes and identifies changed or missing formulas, unexpected formulas, incorrect cells and sheet changes. An untouched copy still fails because the requested edits are missing.

Open the actual result in Excel or LibreOffice, recalculate it and complete the human checks in a copy of `measured.csv`. Check that the subtotal equals the sum of quantity times unit price from the actual edited rows, the charge equals one tenth of that subtotal, and the total is their sum. `openpyxl` reads and writes formula text; it does not calculate formulas. Inspect formatting as well. Passing this small workbook does not establish safety for macros, named ranges, external links, pivots or complex workbooks.
