"""Keep preparation separate from results and protect existing local work."""

from pathlib import Path

import pytest

from scripts.build_index import END, START, build_index
from scripts.excel import check_workbook
from scripts.prepare import KITS, prepare_kit, prepare_note


@pytest.mark.parametrize("kit", (None, *KITS))
def test_existing_work_is_never_overwritten(tmp_path, kit):
    """An existing folder may contain valuable work even without a model output."""
    saved = tmp_path / "scoring.csv"
    saved.write_text("Existing local work must stay unchanged.\n")
    with pytest.raises(FileExistsError):
        if kit is None:
            prepare_note(tmp_path)
        else:
            prepare_kit(kit, tmp_path)
    assert saved.read_text() == "Existing local work must stay unchanged.\n"
    assert list(tmp_path.iterdir()) == [saved]


def test_blank_draft_does_not_become_a_published_note(tmp_path):
    """Copying a template must not add an unfinished note to the README table."""
    (tmp_path / "notes").mkdir()
    (tmp_path / "README.md").write_text(f"{START}\n{END}\n")
    draft = tmp_path / "runs/draft"
    prepare_note(draft)
    assert (draft / "note.md").read_bytes() == Path("TEMPLATE.md").read_bytes()
    assert build_index(tmp_path) == 0
    assert not list((tmp_path / "notes").iterdir())


def test_dictionary_agents_get_separate_inputs_and_the_same_full_prompt(tmp_path):
    """One agent's edits must not change the other's starting files or the prompt."""
    output = tmp_path / "dictionary"
    prepare_kit("data-dictionary", output)
    original = Path("kits/data-dictionary/inputs/schema.sql").read_bytes()
    (output / "copilot/workspace/schema.sql").write_text("Changed in one workspace")
    assert (output / "claude/workspace/schema.sql").read_bytes() == original
    assert (output / "inputs/schema.sql").read_bytes() == original
    prompt = (output / "prompt.txt").read_text()
    for name in ("schema.sql", "requests.csv", "services.csv"):
        assert Path("kits/data-dictionary/inputs", name).read_text() in prompt
    assert not list(output.rglob("dictionary.csv"))


def test_excel_preparation_creates_inputs_without_claiming_success(tmp_path):
    """The untouched starting workbook must still fail the requested-edit check."""
    output = tmp_path / "excel"
    prepare_kit("excel-formulas", output)
    baseline, candidate = output / "baseline.xlsx", output / "workspace/candidate.xlsx"
    assert baseline.read_bytes() == candidate.read_bytes()
    result = check_workbook(baseline, candidate)
    assert result["formulas_unchanged"]
    assert not result["requested_edits_correct"]
    assert not result["passed"]
    assert not (output / "measured.csv").exists()


@pytest.mark.parametrize(("kit", "inputs"), [
    ("local-model", ("workshop.txt",)),
    ("structured-stories", ("brief.txt", "schema.json")),
])
def test_prepared_text_prompts_include_the_task_inputs(tmp_path, kit, inputs):
    """A prepared prompt must include the source material needed to answer it."""
    output = tmp_path / kit
    prepare_kit(kit, output)
    prompt = (output / "prompt.txt").read_text()
    for name in inputs:
        assert Path("kits", kit, "inputs", name).read_text() in prompt
    assert not list(output.rglob("output.txt"))
