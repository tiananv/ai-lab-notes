"""Measure transcription word errors against the words actually spoken."""

import argparse
import json
from pathlib import Path
import re

from scripts.common import cli, write_csv


def word_error_rate(reference: str, transcript: str) -> dict:
    """Calculate word-level edit distance, ignoring case and punctuation only."""
    tokens = lambda text: re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)
    wanted, actual = tokens(reference), tokens(transcript)
    if not wanted:
        raise ValueError("Reference transcript must contain words")
    previous = list(range(len(actual) + 1))
    for row, word in enumerate(wanted, 1):
        current = [row]
        for column, other in enumerate(actual, 1):
            current.append(min(current[-1] + 1, previous[column] + 1,
                               previous[column - 1] + (word != other)))
        previous = current
    return {"reference_words": len(wanted), "word_errors": previous[-1],
            "word_error_rate": previous[-1] / len(wanted)}


def main() -> None:
    """Score a real transcription and retain blank human requirement checks."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--transcript", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = word_error_rate(args.reference.read_text(encoding="utf-8"),
                             args.transcript.read_text(encoding="utf-8"))
    row = {**result, "critical_terms_correct": "", "requirements_correct": "", "reviewer_notes": ""}
    write_csv(args.output, list(row), [row])
    print(json.dumps(result))


if __name__ == "__main__":
    cli(main)
