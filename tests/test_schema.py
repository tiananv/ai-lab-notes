"""Exercise strict schema scoring and incomplete planned batches."""

import json
from pathlib import Path

import pytest

from scripts.schema_score import check_response, score_trials

SCHEMA = json.loads(Path("kits/structured-stories/inputs/schema.json").read_text())
VALID = Path("tests/fixtures/responses/valid-story.json").read_text()


def test_valid_and_semantically_unchecked_fixture():
    """Verify valid and semantically unchecked fixture."""
    assert check_response(VALID, SCHEMA)["valid_schema"] is True


def test_invalid_schema_fixture():
    """Verify invalid schema fixture."""
    result = check_response(Path("tests/fixtures/responses/invalid-story.json").read_text(), SCHEMA)
    assert result["valid_json"] is True
    assert result["valid_schema"] is False


@pytest.mark.parametrize("text", ["```json\n" + VALID + "```", "{", "{\"a\":NaN}",
                                  "{\"stories\":[],\"stories\":[]}", ""])
def test_json_is_never_repaired(text):
    """Verify json is never repaired."""
    assert check_response(text, SCHEMA)["valid_json"] is False


def test_missing_trials_do_not_produce_a_final_rate(tmp_path):
    """Verify missing trials do not produce a final rate."""
    trial = tmp_path / "trial-01"
    trial.mkdir()
    (trial / "output.txt").write_text(VALID)
    rows, summary = score_trials(tmp_path, SCHEMA, 2)
    assert summary == {"expected": 2, "completed": 1, "valid": 1,
                       "status": "incomplete", "validity_rate": None}
    assert rows[1]["status"] == "missing" and rows[1]["semantic_score"] == ""
    second = tmp_path / "trial-02"
    second.mkdir()
    (second / "output.txt").write_text("not JSON")
    _, summary = score_trials(tmp_path, SCHEMA, 2)
    assert summary["validity_rate"] == 0.5


def test_zero_expected_is_invalid(tmp_path):
    """Verify zero expected is invalid."""
    with pytest.raises(ValueError):
        score_trials(tmp_path, SCHEMA, 0)
