"""Copy a blank note template or set up a kit in a fresh local folder."""

import argparse
from pathlib import Path
import shutil

from scripts.common import cli
from scripts.excel import create_workbook
from scripts.llm import compose_prompt

ROOT = Path(__file__).resolve().parents[1]
KITS = ("local-model", "cps230-context", "data-dictionary", "structured-stories",
        "excel-formulas", "voice-requirements")
PROMPT_INPUTS = {
    "local-model": ("workshop.txt",),
    "data-dictionary": ("schema.sql", "requests.csv", "services.csv"),
    "structured-stories": ("brief.txt", "schema.json"),
}


def prepare_note(output: Path) -> None:
    """Copy the unchanged blank template without writing or publishing a note."""
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(ROOT / "TEMPLATE.md", output / "note.md")


def prepare_kit(kit: str, output: Path) -> None:
    """Copy inputs and blank scoring forms, without calling a model or scoring it."""
    if kit not in KITS:
        raise ValueError(f"Choose a kit from {', '.join(KITS)}")
    source = ROOT / "kits" / kit
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(ROOT / "docs/RUN_RECORD.md", output / "RUN_RECORD.md")
    shutil.copyfile(source / "scoring.csv", output / "scoring.csv")
    shutil.copytree(source / "inputs", output / "inputs")
    for prompt in source.glob("*.txt"):
        shutil.copyfile(prompt, output / prompt.name)
    if kit in PROMPT_INPUTS:
        prompt = compose_prompt(source / "prompt.txt",
                                [source / "inputs" / name for name in PROMPT_INPUTS[kit]])
        (output / "prompt.txt").write_text(prompt, encoding="utf-8")
    if kit == "data-dictionary":
        for tool in ("copilot", "claude"):
            shutil.copytree(source / "inputs", output / tool / "workspace")
    elif kit == "excel-formulas":
        create_workbook(source / "inputs/orders.csv", output / "baseline.xlsx")
        (output / "workspace").mkdir()
        shutil.copyfile(output / "baseline.xlsx", output / "workspace/candidate.xlsx")
    elif kit == "voice-requirements":
        shutil.copyfile(source / "inputs/reading.txt", output / "reference.txt")


def main() -> None:
    """Prepare a blank draft or a kit, leaving existing folders untouched."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    note = commands.add_parser("note", help="Copy the blank note template")
    note.add_argument("--out", type=Path, required=True)
    kit = commands.add_parser("kit", help="Copy kit inputs and blank scoring forms")
    kit.add_argument("kit", choices=KITS)
    kit.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError("That folder already exists. Choose a fresh --out to keep earlier work.")
    if args.command == "note":
        prepare_note(args.out)
        print(f"Blank template copied: {args.out / 'note.md'}. Fill it after a real experiment.")
    else:
        prepare_kit(args.kit, args.out)
        print(f"Kit ready: {args.out}. No model called and no results recorded.")
        print(f"Follow kits/{args.kit}/README.md to run it and score the actual output.")


if __name__ == "__main__":
    cli(main)
