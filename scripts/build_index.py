"""Validate note front matter and rebuild the README notes table."""

import argparse
from datetime import date
from html import escape
from pathlib import Path
import re

import yaml

from scripts.common import cli

VERDICTS = ("worth-it", "maybe", "not-yet")
START, END = "<!-- NOTES:START -->", "<!-- NOTES:END -->"


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


def read_note(path: Path) -> dict:
    """Validate the dated filename and required front matter, including the pre-run rule."""
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
    return {**meta, "date": note_date.isoformat(), "filename": path.name}


def _cell(value: str) -> str:
    value = escape(value, quote=True).replace("|", "&#124;")
    for char in ("[", "]", "*", "_", "`", "\\"):
        value = value.replace(char, f"&#{ord(char)};")
    return value


def build_index(root: Path) -> int:
    """Replace only the generated block with a notes table or a pending message."""
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
        block = "\n".join(rows)
    else:
        block = "**First note coming soon.**"
    readme.write_text(before + START + "\n\n" + block + "\n\n" + END + after,
                      encoding="utf-8")
    return len(notes)


def main() -> None:
    """Build the index from the repository root or an explicit test root."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    count = build_index(args.root)
    print(f"Indexed {count} notes.")


if __name__ == "__main__":
    cli(main)
