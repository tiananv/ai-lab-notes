"""Validate genuine notes and rebuild the README index and activity charts."""

import argparse
from collections import Counter
from datetime import date
from html import escape
import os
from pathlib import Path
import re

import yaml

from scripts.common import cli

VERDICTS = ("worth-it", "maybe", "not-yet")
SECTIONS = ("The question", "Verdict", "What I'd tell another BA", "Setup", "What happened")
START, END = "<!-- NOTES:START -->", "<!-- NOTES:END -->"
THEMES = {
    "light": ("#1c1e22", "#5e646d", "#2f5bd0", "#157a5d", "#995c00", "#e5e1d9"),
    "dark": ("#e8e9ec", "#a3a9b2", "#8eaaff", "#62cfa9", "#efb45c", "#2c3139"),
}


class UniqueLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects ambiguous duplicate metadata keys."""


def _mapping(loader: UniqueLoader, node: yaml.MappingNode) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError("Front matter keys must be unique strings")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def _section_titles(body: str) -> tuple[str, ...]:
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    titles, fence = [], ""
    for line in body.splitlines():
        if fence:
            if re.fullmatch(rf" {{0,3}}{re.escape(fence[0])}{{{len(fence)},}}[ \t]*", line):
                fence = ""
            continue
        marker = re.match(r" {0,3}(`{3,}|~{3,})", line)
        if marker:
            fence = marker[1]
        elif line.startswith("## "):
            titles.append(line[3:].strip())
    return tuple(titles)


def read_note(path: Path) -> dict:
    """Validate note metadata, including the pre-run rule, and answer-first sections."""
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2})-[a-z0-9]+(?:-[a-z0-9]+)*\.md", path.name)
    if not match:
        raise ValueError(f"{path.name}: use YYYY-MM-DD-slug.md")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError(f"{path.name}: YAML front matter must start and end with ---")
    end = lines.index("---", 1)
    try:
        meta = yaml.load("\n".join(lines[1:end]), Loader=UniqueLoader)
    except yaml.YAMLError as error:
        raise ValueError(f"{path.name}: invalid YAML front matter") from error
    required = {"date", "title", "question", "verdict", "decision_rule", "tools", "time_spent", "tags"}
    if not isinstance(meta, dict) or not required <= meta.keys():
        raise ValueError(f"{path.name}: required fields are {', '.join(sorted(required))}")
    try:
        note_date = date.fromisoformat(str(meta["date"]))
    except ValueError as error:
        raise ValueError(f"{path.name}: date must be YYYY-MM-DD") from error
    if note_date.isoformat() != match[1]:
        raise ValueError(f"{path.name}: date must match the filename")
    for key in ("title", "question", "verdict", "decision_rule", "time_spent"):
        if not isinstance(meta[key], str) or not meta[key].strip() or "\n" in meta[key]:
            raise ValueError(f"{path.name}: {key} must be non-empty, single-line text")
    if meta["verdict"] not in VERDICTS:
        raise ValueError(f"{path.name}: verdict must be {', '.join(VERDICTS)}")
    if not re.fullmatch(r"[1-9]\d* (?:min|h)", meta["time_spent"]):
        raise ValueError(f"{path.name}: time_spent must look like 45 min or 1 h")
    for key in ("tools", "tags"):
        values = meta[key]
        if not isinstance(values, list) or not values or any(
            not isinstance(item, str) or not item.strip() or "\n" in item for item in values
        ):
            raise ValueError(f"{path.name}: {key} must be a non-empty list of strings")
    body = "\n".join(lines[end + 1:])
    if not body.strip():
        raise ValueError(f"{path.name}: note body is empty")
    if _section_titles(body) != SECTIONS:
        raise ValueError(f"{path.name}: required sections in order: {', '.join(SECTIONS)}")
    return {**meta, "date": note_date.isoformat(), "filename": path.name}


def _cell(value: str) -> str:
    value = escape(value, quote=True).replace("|", "&#124;")
    for char in ("[", "]", "*", "_", "`", "\\"):
        value = value.replace(char, f"&#{ord(char)};")
    return value


def _picture(stem: str, alt: str) -> str:
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" '
            f'srcset="assets/{stem}-dark.svg">\n'
            f'  <img src="assets/{stem}-light.svg" alt="{alt}">\n</picture>')


def _charts(notes: list[dict], assets: Path) -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(Path(".cache/matplotlib").resolve()))
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    assets.mkdir(parents=True, exist_ok=True)
    counts = Counter(note["date"][:7] for note in notes)
    month = date.fromisoformat(min(counts) + "-01")
    last = max(counts)
    months = []
    while month.strftime("%Y-%m") <= last:
        months.append(month.strftime("%Y-%m"))
        month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
    verdicts = Counter(note["verdict"] for note in notes)
    for theme, (ink, muted, blue, green, amber, line) in THEMES.items():
        with plt.rc_context({"svg.hashsalt": "ai-lab-notes", "svg.fonttype": "none",
                             "font.family": "DejaVu Sans", "font.size": 11}):
            for stem, labels, values, colours, title in (
                ("activity", months, [counts[m] for m in months], blue, "Notes per month"),
                ("verdicts", list(VERDICTS), [verdicts[v] for v in VERDICTS],
                 [green, amber, blue], "Verdicts in published notes"),
            ):
                fig, ax = plt.subplots(figsize=(8, 3), layout="constrained")
                ax.bar(labels, values, color=colours, width=0.55)
                ax.set_title(title, color=ink, loc="left", pad=16)
                ax.set_ylabel("Notes", color=muted)
                ax.tick_params(colors=muted, length=0)
                ax.yaxis.set_major_locator(MaxNLocator(integer=True))
                ax.set_ylim(0, max(values) + 1)
                ax.spines[["top", "right"]].set_visible(False)
                for side in ("bottom", "left"):
                    ax.spines[side].set_color(line)
                if len(labels) > 6:
                    ax.tick_params(axis="x", labelrotation=45)
                fig.savefig(assets / f"{stem}-{theme}.svg", transparent=True,
                            metadata={"Date": None, "Title": title})
                plt.close(fig)


def build_index(root: Path) -> int:
    """Replace only the generated block; produce no charts for an empty notebook."""
    readme = root / "README.md"
    original = readme.read_text(encoding="utf-8")
    if original.count(START) != 1 or original.count(END) != 1:
        raise ValueError("README must contain exactly one pair of NOTES markers")
    before, remainder = original.split(START)
    if END not in remainder:
        raise ValueError("NOTES markers are out of order")
    _, after = remainder.split(END)
    folder = root / "notes"
    if not folder.is_dir():
        raise ValueError("notes/ is missing")
    paths = sorted(folder.glob("*.md"))
    notes = sorted((read_note(path) for path in paths),
                   key=lambda note: (note["date"], note["filename"]), reverse=True)
    if notes:
        rows = ["| Date | Title | Verdict | Tools |", "| --- | --- | --- | --- |"]
        for note in notes:
            title = f'[{_cell(note["title"])}](notes/{note["filename"]})'
            rows.append(f'| {note["date"]} | {title} | {note["verdict"]} | '
                        f'{_cell(", ".join(note["tools"]))} |')
        _charts(notes, root / "assets")
        block = "\n".join(rows) + "\n\n" + _picture("activity", "Notes per month")
        block += "\n\n" + _picture("verdicts", "Number of notes with each verdict")
    else:
        block = ("**First note coming soon.** The experiment kits and scoring sheets are ready. "
                 "Experiment results are pending.\n\nRun a [kit](BACKLOG.md), score the actual "
                 "output, then write a note using [TEMPLATE.md](TEMPLATE.md). "
                 "Run `make results` to refresh this index and its charts.")
        for stem in ("activity", "verdicts"):
            for theme in THEMES:
                (root / "assets" / f"{stem}-{theme}.svg").unlink(missing_ok=True)
    readme.write_text(before + START + "\n\n" + block + "\n\n" + END + after,
                      encoding="utf-8")
    return len(notes)


def main() -> None:
    """Build the index from the repository root or an explicit test root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    count = build_index(args.root)
    print(f"Indexed {count} notes; " + ("charts generated." if count else "no charts generated."))


if __name__ == "__main__":
    cli(main)
