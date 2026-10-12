"""Check front matter validation and reproducible notes tables with synthetic inputs."""

from pathlib import Path
import shutil

import pytest

from scripts.build_index import build_index, read_note, START, END

FIXTURES = Path("tests/fixtures/notes")


def root(tmp_path, populated=False):
    """Prepare an isolated notebook, keeping synthetic fixtures away from real notes."""
    (tmp_path / "notes").mkdir()
    (tmp_path / "README.md").write_text(f"Before\n{START}\nstale\n{END}\nAfter\n")
    if populated:
        for note in FIXTURES.glob("*.md"):
            shutil.copy(note, tmp_path / "notes" / note.name)
    return tmp_path


def test_empty_index_has_no_charts_and_preserves_surroundings(tmp_path):
    """Verify empty index has no charts and preserves surroundings."""
    project = root(tmp_path)
    assert build_index(project) == 0
    text = (project / "README.md").read_text()
    assert "First note coming soon" in text
    assert text.startswith("Before\n") and text.endswith("\nAfter\n")
    assert "<picture>" not in text
    assert not list((project / "assets").glob("*.svg"))
    assert not list((project / "notes").iterdir())


def test_index_sorts_notes_without_charts_and_is_deterministic(tmp_path):
    """Keep the plain notes table stable and leave chart assets uncreated."""
    project = root(tmp_path, True)
    assert build_index(project) == 2
    text = (project / "README.md").read_text()
    assert text.index("2026-03-06") < text.index("2026-01-05")
    assert "notes/2026-03-06-beta.md" in text
    assert "| Date | Title | Verdict | Tools |" in text
    assert "| worth-it | mock-tool v0 |" in text
    assert "<picture>" not in text
    assert not (project / "assets").exists()
    build_index(project)
    assert text == (project / "README.md").read_text()


@pytest.mark.parametrize(("old", "new"), [
    ("verdict: worth-it", "verdict: amazing"),
    ("verdict: worth-it", ""),
    ("verdict: worth-it", 'verdict: ""'),
    ("tools: [\"mock-tool v0\"]", "tools: mock-tool"),
    ("tags: [fixture]", "tags: []"),
    ("time_spent: \"1 min\"", "time_spent: yesterday"),
    ("date: 2026-01-05", "date: 2026-02-30"),
    ("date: 2026-01-05", "date: 2026-01-06"),
    ("verdict: worth-it", "verdict: worth-it\nverdict: maybe"),
    ("question:", "other:"),
    ("tags: [fixture]", "tags: [true]"),
])
def test_bad_front_matter_fails(tmp_path, old, new):
    """Verify bad front matter fails."""
    source = FIXTURES / "2026-01-05-alpha.md"
    path = tmp_path / source.name
    path.write_text(source.read_text().replace(old, new))
    with pytest.raises(ValueError):
        read_note(path)


@pytest.mark.parametrize("value", [None, "", '""', '"   "', "true", "2", "[]", "{}", "|\n  two\n  lines"])
def test_decision_rule_is_required_text_before_indexing(tmp_path, value):
    """Reject missing, blank or non-text rules without replacing the published index."""
    project = root(tmp_path, True)
    build_index(project)
    readme = project / "README.md"
    before = readme.read_bytes()
    note = project / "notes/2026-01-05-alpha.md"
    lines = note.read_text().splitlines()
    lines = [line if not line.startswith("decision_rule:") else
             f"decision_rule: {value}" for line in lines
             if value is not None or not line.startswith("decision_rule:")]
    note.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError, match="decision_rule"):
        build_index(project)
    assert readme.read_bytes() == before


@pytest.mark.parametrize("body", [
    "",
    "Synthetic parser input with no headings.\n",
    "## Setup\n\n## What happened\n\n## Verdict\n\n## The question\n",
    "## Different headings\n\n### Detail\n\n```markdown\n## Quoted output\n```\n",
])
def test_index_accepts_front_matter_without_a_fixed_body(tmp_path, body):
    """Leave body writing to the notebook owner while still indexing valid metadata."""
    project = root(tmp_path)
    source = FIXTURES / "2026-01-05-alpha.md"
    header = source.read_text().split("\n## ", 1)[0]
    note = project / "notes" / source.name
    note.write_text(header + "\n" + body)
    assert build_index(project) == 1
    assert f"notes/{source.name}" in (project / "README.md").read_text()


def test_bad_filename_and_missing_front_matter_fail(tmp_path):
    """Verify bad filename and missing front matter fail."""
    path = tmp_path / "not-dated.md"
    path.write_text("hello")
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        read_note(path)
    dated = tmp_path / "2026-01-05-test.md"
    dated.write_text("hello")
    with pytest.raises(ValueError, match="front matter"):
        read_note(dated)


def test_invalid_note_does_not_modify_readme(tmp_path):
    """Verify invalid note does not modify readme."""
    project = root(tmp_path)
    readme = project / "README.md"
    before = readme.read_bytes()
    (project / "notes/invalid.md").write_text("Not a note")
    with pytest.raises(ValueError):
        build_index(project)
    assert readme.read_bytes() == before


@pytest.mark.parametrize("markers", [START, END + START, START + END + END])
def test_bad_markers_fail_without_changing_file(tmp_path, markers):
    """Verify bad markers fail without changing file."""
    project = root(tmp_path)
    readme = project / "README.md"
    readme.write_text(markers)
    with pytest.raises(ValueError):
        build_index(project)
    assert readme.read_text() == markers


def test_title_escapes_table_and_link_markup(tmp_path):
    """Verify title escapes table and link markup."""
    project = root(tmp_path)
    source = FIXTURES / "2026-01-05-alpha.md"
    (project / "notes" / source.name).write_text(source.read_text().replace(
        "Synthetic parser fixture A", "A | [bad](url) <b>"))
    build_index(project)
    text = (project / "README.md").read_text()
    assert "&#124;" in text and "&lt;b&gt;" in text and "&#91;bad&#93;" in text
