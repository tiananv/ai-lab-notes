"""Shared file writers and concise command-line error reporting."""

import csv
import json
from pathlib import Path
from typing import Callable


def write_json(path: Path, value: object) -> None:
    """Write a readable JSON file, creating its parent directory."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    """Write a CSV with a fixed column order, including an empty sheet's header."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def cli(action: Callable[[], int | None]) -> None:
    """Exit cleanly for expected input and filesystem errors."""
    try:
        code = action()
    except (ValueError, OSError) as error:
        print(f"Error: {error}")
        raise SystemExit(2) from None
    raise SystemExit(code or 0)
