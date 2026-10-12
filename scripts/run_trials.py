"""Prepare or run a predeclared set of independent, identical text prompts."""

import argparse
import os
from pathlib import Path

from scripts.common import cli
from scripts.llm import BACKENDS, compose_prompt, run


def main() -> None:
    """Run each planned trial once; manual trials wait for real pasted answers."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", type=Path, required=True)
    parser.add_argument("--input", type=Path, action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--backend", choices=BACKENDS, default=os.getenv("LLM_BACKEND", "manual"))
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", ""))
    args = parser.parse_args()
    if args.trials < 1:
        raise ValueError("--trials must be positive")
    targets = [args.out / f"trial-{i:02d}" for i in range(1, args.trials + 1)]
    if any((target / "output.txt").exists() for target in targets):
        raise ValueError("A trial already has an output. Use a fresh --out for a new batch.")
    prompt = compose_prompt(args.prompt, args.input)
    for target in targets:
        meta = run(prompt, target, args.backend, args.model)
        print(f'{target}: {meta["status"]}')


if __name__ == "__main__":
    cli(main)
