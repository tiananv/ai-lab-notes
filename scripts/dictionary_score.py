"""Compare an actual dictionary CSV with the kit's known SQLite structure."""

import argparse
import csv
import json
from pathlib import Path
import sqlite3

from scripts.common import cli, write_csv, write_json


def expected_columns(schema: Path) -> dict:
    """Read the bundled DDL in memory to derive column names, types and nullability."""
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(schema.read_text(encoding="utf-8"))
        tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        result = {}
        for (table,) in tables:
            quoted = table.replace('"', '""')
            for _, column, dtype, not_null, _, _ in connection.execute(f'PRAGMA table_info("{quoted}")'):
                result[(table, column)] = (dtype.upper(), "no" if not_null else "yes")
        return result
    finally:
        connection.close()


def score_dictionary(schema: Path, candidate: Path) -> tuple[list[dict], dict]:
    """Check coverage and structural facts; leave business meanings for a person."""
    expected = expected_columns(schema)
    with candidate.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = {"table", "column", "data_type", "nullable", "description", "assumption"}
        if set(reader.fieldnames or []) != fields or len(reader.fieldnames) != len(fields):
            raise ValueError("Dictionary CSV needs exactly: " + ", ".join(sorted(fields)))
        actual = list(reader)
    seen, rows = set(), []
    for row in actual:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("Dictionary CSV contains a malformed row")
        key = row["table"], row["column"]
        correct = expected.get(key) == (row["data_type"].upper(), row["nullable"].lower())
        rows.append({"table": key[0], "column": key[1], "present": True,
                     "structure_correct": correct, "duplicate": key in seen,
                     "description_present": bool(row["description"].strip()),
                     "meaning_score": "", "reviewer_notes": ""})
        seen.add(key)
    for table, column in sorted(expected.keys() - seen):
        rows.append({"table": table, "column": column, "present": False,
                     "structure_correct": False, "duplicate": False,
                     "description_present": False, "meaning_score": "", "reviewer_notes": ""})
    summary = {"expected_columns": len(expected), "covered_columns": len(expected.keys() & seen),
               "extra_columns": len(seen - expected.keys()),
               "structural_pass": all(row["structure_correct"] and not row["duplicate"] for row in rows)}
    return rows, summary


def main() -> None:
    """Write a structural score sheet for one independently completed agent task."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=Path("kits/data-dictionary/inputs/schema.sql"))
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows, summary = score_dictionary(args.schema, args.candidate)
    write_csv(args.output, list(rows[0]), rows)
    write_json(args.output.with_suffix(".json"), summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    cli(main)
