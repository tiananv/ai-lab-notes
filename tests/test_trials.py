"""Exercise batch preparation and refusal to silently repeat completed trials."""

import json
from pathlib import Path
import sys

import pytest

from scripts.run_trials import main


def test_manual_batch_has_identical_prompts_and_no_answers(tmp_path, monkeypatch):
    """Verify preparation cannot manufacture a completed response or repeat one."""
    monkeypatch.setattr(sys, "argv", ["run_trials", "--prompt",
        "kits/structured-stories/prompt.txt", "--input", "kits/structured-stories/inputs/brief.txt",
        "--input", "kits/structured-stories/inputs/schema.json", "--out", str(tmp_path),
        "--trials", "3", "--backend", "manual", "--model", "synthetic-test-model"])
    main()
    records = [json.loads(path.read_text()) for path in tmp_path.glob("*/metadata.json")]
    assert len(records) == 3
    assert len({row["prompt_sha256"] for row in records}) == 1
    assert all(row["status"] == "awaiting-answer" for row in records)
    assert not list(tmp_path.glob("*/output.txt"))
    (tmp_path / "trial-01/output.txt").write_bytes(Path("tests/fixtures/responses/manual.txt").read_bytes())
    with pytest.raises(ValueError, match="already has an output"):
        main()
