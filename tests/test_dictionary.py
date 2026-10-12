"""Check structural dictionary scoring against the known fictional DDL."""

from pathlib import Path

import pytest

from scripts.common import write_csv
from scripts.dictionary_score import expected_columns, score_dictionary

SCHEMA = Path("kits/data-dictionary/inputs/schema.sql")


def test_structure_coverage_extras_duplicates_and_meaning_are_separate(tmp_path):
    """Verify structure coverage extras duplicates and meaning are separate."""
    expected = expected_columns(SCHEMA)
    rows = [{"table": table, "column": column, "data_type": dtype, "nullable": nullable,
             "description": "Synthetic test description", "assumption": ""}
            for (table, column), (dtype, nullable) in expected.items()]
    candidate = tmp_path / "dictionary.csv"
    write_csv(candidate, list(rows[0]), rows)
    measured, summary = score_dictionary(SCHEMA, candidate)
    assert summary["structural_pass"] is True and summary["expected_columns"] == 9
    assert all(row["meaning_score"] == "" for row in measured)
    rows.pop()
    rows.append({**rows[0], "column": "invented"})
    rows.append(rows[0])
    write_csv(candidate, list(rows[0]), rows)
    measured, summary = score_dictionary(SCHEMA, candidate)
    assert summary["structural_pass"] is False and summary["extra_columns"] == 1
    assert any(not row["present"] for row in measured)
    assert any(row["duplicate"] for row in measured)


def test_nullability_is_from_schema_not_sample(tmp_path):
    """Verify nullability is from schema not sample."""
    expected = expected_columns(SCHEMA)
    assert expected[("requests", "closure_reason")] == ("TEXT", "yes")
    assert expected[("requests", "request_id")] == ("INTEGER", "no")


def test_bad_csv_is_not_repaired(tmp_path):
    """Verify bad csv is not repaired."""
    candidate = tmp_path / "bad.csv"
    candidate.write_text("column,description\nexample,example\n")
    with pytest.raises(ValueError, match="exactly"):
        score_dictionary(SCHEMA, candidate)
