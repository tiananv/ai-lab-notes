"""Check metadata contracts and reproducible chart/index behaviour on fixture files."""

from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

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


def test_index_sorts_counts_gap_months_and_is_deterministic(tmp_path):
    """Verify index sorts counts gap months and is deterministic."""
    project = root(tmp_path, True)
    assert build_index(project) == 2
    text = (project / "README.md").read_text()
    assert text.index("2026-03-06") < text.index("2026-01-05")
    assert "notes/2026-03-06-beta.md" in text
    charts = list((project / "assets").glob("*.svg"))
    assert len(charts) == 4
    assert "2026-02" in (project / "assets/activity-light.svg").read_text()
    original = {path.name: path.read_bytes() for path in charts}
    for chart in charts:
        ET.parse(chart)
        assert "<dc:date>" not in chart.read_text()
    build_index(project)
    assert text == (project / "README.md").read_text()
    assert original == {path.name: path.read_bytes() for path in charts}
    for note in (project / "notes").glob("*.md"):
        note.unlink()
    build_index(project)
    assert not list((project / "assets").glob("*.svg"))


@pytest.mark.parametrize(("old", "new"), [
    ("verdict: worth-it", "verdict: amazing"),
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
