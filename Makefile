export UV_CACHE_DIR := $(CURDIR)/.cache/uv
export UV_PYTHON_INSTALL_DIR := $(CURDIR)/.cache/python
export MPLCONFIGDIR := $(CURDIR)/.cache/matplotlib

.PHONY: setup test index results cps230 excel

setup:
	uv sync --locked

test:
	uv run --locked pytest

index:
	uv run --locked python -m scripts.build_index

results: index

cps230:
	uv run --locked python -m scripts.cps230 download

excel:
	uv run --locked python -m scripts.excel create --output runs/excel/baseline.xlsx
