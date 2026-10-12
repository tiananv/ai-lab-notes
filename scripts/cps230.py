"""Download the public standard and prepare whole-document or search prompts."""

import argparse
import csv
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import re
from urllib.error import URLError
from urllib.request import Request, urlopen

from pypdf import PdfReader

from scripts.common import cli, write_json
from scripts.llm import sha256

KIT = Path("kits/cps230-context")
RAW = Path("data/raw/cps230")


def download(source_path: Path, destination: Path) -> dict:
    """Save a public PDF and its source fingerprint outside the publishable tree."""
    source = json.loads(source_path.read_text(encoding="utf-8"))
    pdf = destination / "standard.pdf"
    if pdf.exists():
        manifest_path = destination / "manifest.json"
        if not manifest_path.exists():
            raise ValueError("Cached PDF has no manifest; use a fresh --raw directory.")
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        digest = sha256(pdf.read_bytes())
        if (digest != manifest.get("sha256") or manifest.get("pdf_url") != source["pdf_url"]
                or (source.get("sha256") and digest != source["sha256"])):
            raise ValueError("Cached PDF does not match the source; review it before downloading again.")
        return manifest
    try:
        request = Request(source["pdf_url"], headers={"User-Agent": "ai-lab-notes/0.1 (public research)"})
        with urlopen(request, timeout=60) as response:
            data = response.read(10_000_001)
    except (URLError, TimeoutError, OSError):
        raise ValueError("APRA download failed. Check the source link and retry later.") from None
    if len(data) > 10_000_000 or not data.startswith(b"%PDF-"):
        raise ValueError("APRA download was not a PDF within the expected size limit")
    digest = sha256(data)
    if source.get("sha256") and digest != source["sha256"]:
        raise ValueError("APRA PDF has changed. Review the edition and source hash before running.")
    reader = PdfReader(io.BytesIO(data))
    manifest = {**source, "sha256": digest, "pages": len(reader.pages),
                "downloaded_at_utc": datetime.now(timezone.utc).isoformat()}
    destination.mkdir(parents=True, exist_ok=True)
    pdf.write_bytes(data)
    write_json(destination / "manifest.json", manifest)
    return manifest


def select_pages(pages: list[str], question: str, mode: str, top_k: int = 3) -> list[int]:
    """Select all pages or rank pages by distinct query-word overlap, with stable ties."""
    if not pages or top_k < 1:
        raise ValueError("Pages and a positive top_k are required")
    if mode == "long-context":
        return list(range(len(pages)))
    if mode != "search":
        raise ValueError("Mode must be long-context or search")
    stopwords = {"the", "a", "an", "and", "or", "to", "of", "in", "for", "is", "what", "must"}
    terms = set(re.findall(r"[a-z0-9]+", question.lower())) - stopwords
    scores = [len(terms & set(re.findall(r"[a-z0-9]+", page.lower()))) for page in pages]
    return sorted(range(len(pages)), key=lambda index: (-scores[index], index))[:top_k]


def prepare(raw: Path, output: Path, mode: str) -> int:
    """Build prompts from verified PDF bytes without running a model or scoring answers."""
    data = (raw / "standard.pdf").read_bytes()
    manifest = json.loads((raw / "manifest.json").read_text(encoding="utf-8"))
    source = json.loads((KIT / "inputs/source.json").read_text(encoding="utf-8"))
    digest = sha256(data)
    if digest != manifest["sha256"] or (source.get("sha256") and digest != source["sha256"]):
        raise ValueError("PDF does not match its recorded source hash")
    pages = [page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages]
    if any(not page.strip() for page in pages):
        raise ValueError("A PDF page has no extractable text. Review extraction before using it.")
    with (KIT / "inputs/questions.csv").open(newline="", encoding="utf-8") as stream:
        questions = list(csv.DictReader(stream))
    if output.exists():
        raise ValueError("Prompt directory already exists; choose a fresh --out")
    instructions = (KIT / "prompt.txt").read_text(encoding="utf-8")
    output.mkdir(parents=True)
    for row in questions:
        selected = select_pages(pages, row["question"], mode)
        context = "\n\n".join(f"[PDF page {index + 1}]\n{pages[index]}" for index in selected)
        prompt = f'{instructions}\n\nQuestion: {row["question"]}\n\nSource:\n{context}'
        (output / f'{row["id"]}.txt').write_text(prompt, encoding="utf-8")
        write_json(output / f'{row["id"]}.context.json', {
            "mode": mode, "source_sha256": digest, "edition": manifest["edition"],
            "pdf_pages": [index + 1 for index in selected], "prompt_characters": len(prompt),
            "prompt_sha256": sha256(prompt.encode("utf-8")),
            "retrieval": "all pages" if mode == "long-context" else "query-word overlap; top 3 pages",
        })
    return len(questions)


def main() -> None:
    """Download CPS 230 or prepare prompts for a controlled comparison."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("download")
    fetch.add_argument("--source", type=Path, default=KIT / "inputs/source.json")
    fetch.add_argument("--raw", type=Path, default=RAW)
    build = sub.add_parser("prepare")
    build.add_argument("--raw", type=Path, default=RAW)
    build.add_argument("--out", type=Path, required=True)
    build.add_argument("--mode", choices=("long-context", "search"), required=True)
    args = parser.parse_args()
    if args.command == "download":
        manifest = download(args.source, args.raw)
        print(f'Public PDF ready: {manifest["pages"]} pages; SHA-256 {manifest["sha256"]}')
    else:
        count = prepare(args.raw, args.out, args.mode)
        print(f"Prepared {count} {args.mode} prompts; no model called.")


if __name__ == "__main__":
    cli(main)
