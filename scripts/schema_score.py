"""Score every planned JSON trial without hiding missing or malformed responses."""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from scripts.common import cli, write_csv, write_json


def _unique(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise ValueError(f"Non-JSON constant: {value}")


def check_response(text: str, schema: dict) -> dict:
    """Check strict JSON and schema conformance, without repairing the answer."""
    Draft202012Validator.check_schema(schema)
    try:
        value = json.loads(text, object_pairs_hook=_unique, parse_constant=_constant)
    except ValueError:
        return {"valid_json": False, "valid_schema": False, "issues": "Invalid JSON"}
    errors = list(Draft202012Validator(schema).iter_errors(value))
    # Report paths and validator names, not potentially private response content.
    issues = "; ".join(f"/{'/'.join(map(str, e.absolute_path))}: {e.validator}" for e in errors)
    return {"valid_json": True, "valid_schema": not errors, "issues": issues}


def score_trials(folder: Path, schema: dict, expected: int) -> tuple[list[dict], dict]:
    """Count all planned trials; leave the final validity rate unset until complete."""
    if expected < 1:
        raise ValueError("--expected must be positive")
    rows = []
    for number in range(1, expected + 1):
        path = folder / f"trial-{number:02d}" / "output.txt"
        measured = check_response(path.read_text(encoding="utf-8"), schema) if path.exists() else {
            "valid_json": "", "valid_schema": "", "issues": "Awaiting actual response"}
        rows.append({"trial": number, "status": "scored" if path.exists() else "missing",
                     **measured, "semantic_score": "", "reviewer_notes": ""})
    completed = sum(row["status"] == "scored" for row in rows)
    valid = sum(row["valid_schema"] is True for row in rows)
    summary = {"expected": expected, "completed": completed, "valid": valid,
               "status": "complete" if completed == expected else "incomplete",
               "validity_rate": valid / expected if completed == expected else None}
    return rows, summary


def main() -> None:
    """Write measurable CSV columns and a summary for planned trial directories."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=Path("kits/structured-stories/inputs/schema.json"))
    parser.add_argument("--expected", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    rows, summary = score_trials(args.runs, schema, args.expected)
    write_csv(args.output, list(rows[0]), rows)
    write_json(args.output.with_suffix(".json"), summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    cli(main)
