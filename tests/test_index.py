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


@pytest.mark.parametrize("value", [None, "", '""', '"   "', "true", "2", "[]", "{}", "|\n  two\n  lines"])
def test_decision_rule_is_required_text_before_indexing(tmp_path, value):
    """Reject missing, blank or non-text rules without replacing the published index."""
    project = root(tmp_path, True)
    build_index(project)
    published = [project / "README.md", *sorted((project / "assets").glob("*.svg"))]
    before = {path: path.read_bytes() for path in published}
    note = project / "notes/2026-01-05-alpha.md"
    lines = note.read_text().splitlines()
    lines = [line if not line.startswith("decision_rule:") else
             f"decision_rule: {value}" for line in lines
             if value is not None or not line.startswith("decision_rule:")]
    note.write_text("\n".join(lines) + "\n")
    with pytest.raises(ValueError, match="decision_rule"):
        build_index(project)
    assert before == {path: path.read_bytes() for path in published}


@pytest.mark.parametrize(("old", "new"), [
    ("## Verdict", "## Setup"),
    ("## Verdict", "### Verdict"),
    ("## Verdict", "## Verdict\n\n## Verdict"),
    ("## Verdict", "<!--\n## Verdict\n-->"),
    ("## Verdict", "```markdown\n## Verdict\n```"),
    ("## Verdict", "~~~markdown\n## Verdict\n~~~"),
    ("## Verdict", ""),
])
def test_required_sections_must_be_visible_and_in_order(tmp_path, old, new):
    """Reject missing, duplicated or out-of-order sections, including hidden headings."""
    source = FIXTURES / "2026-01-05-alpha.md"
    note = tmp_path / source.name
    note.write_text(source.read_text().replace(old, new))
    with pytest.raises(ValueError, match="required sections in order"):
        read_note(note)


def test_old_setup_first_order_fails(tmp_path):
    """Require the answer before setup even when all five sections are present."""
    source = FIXTURES / "2026-01-05-alpha.md"
    header, *_ = source.read_text().split("\n## ")
    old_order = ("The question", "Setup", "What happened", "What I'd tell another BA", "Verdict")
    note = tmp_path / source.name
    note.write_text(header + "".join(f"\n## {title}\n\nFixture only.\n" for title in old_order))
    with pytest.raises(ValueError, match="required sections in order"):
        read_note(note)


def test_extra_detail_does_not_change_section_order(tmp_path):
    """Allow smaller headings and quoted output headings without changing note sections."""
    source = FIXTURES / "2026-01-05-alpha.md"
    note = tmp_path / source.name
    note.write_text(source.read_text() + "\n### Detail\n<!--\n## Comment\n-->\n"
                    "```markdown\n## Quoted output\n```\n~~~\n## More output\n~~~\n")
    assert read_note(note)["verdict"] == "worth-it"


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
