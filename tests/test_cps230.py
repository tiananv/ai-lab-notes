"""Check download handling, source integrity and the fixed search baseline offline."""

import io
import json
from pathlib import Path
from types import SimpleNamespace
from urllib.error import URLError

from pypdf import PdfWriter
import pytest

from scripts import cps230
from scripts.llm import sha256


def test_retrieval_and_stable_ties():
    """Verify retrieval and stable ties."""
    pages = ["incident notify time", "tolerance duration data loss", "incident notify time"]
    assert cps230.select_pages(pages, "incident notify", "search", 2) == [0, 2]
    assert cps230.select_pages(pages, "anything", "long-context") == [0, 1, 2]


def test_download_records_real_bytes_using_mocked_transport(tmp_path, monkeypatch):
    """Verify download records real bytes using mocked transport."""
    output = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.write(output)
    data = output.getvalue()
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"pdf_url": "https://example.invalid/fixture.pdf",
                                  "edition": "fixture", "sha256": sha256(data)}))
    monkeypatch.setattr(cps230, "urlopen", lambda *a, **k: io.BytesIO(data))
    result = cps230.download(source, tmp_path / "raw")
    assert result["sha256"] == sha256(data) and result["pages"] == 1
    assert (tmp_path / "raw/standard.pdf").read_bytes() == data
    def no_download(*args, **kwargs):
        raise AssertionError("A validated cached download needs no network")
    monkeypatch.setattr(cps230, "urlopen", no_download)
    assert cps230.download(source, tmp_path / "raw") == result
    (tmp_path / "raw/standard.pdf").write_bytes(b"altered")
    with pytest.raises(ValueError, match="Cached PDF"):
        cps230.download(source, tmp_path / "raw")


@pytest.mark.parametrize("data", [b"blocked HTML", b"%PDF-unexpected"])
def test_download_rejects_wrong_content_or_hash(tmp_path, monkeypatch, data):
    """Verify download rejects wrong content or hash."""
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"pdf_url": "https://example.invalid/fixture.pdf", "sha256": "wrong"}))
    monkeypatch.setattr(cps230, "urlopen", lambda *a, **k: io.BytesIO(data))
    with pytest.raises(ValueError):
        cps230.download(source, tmp_path / "raw")
    assert not (tmp_path / "raw/standard.pdf").exists()


def test_download_failure_is_actionable(tmp_path, monkeypatch):
    """Verify download failure is actionable."""
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"pdf_url": "https://example.invalid/fixture.pdf"}))
    def fail(*args, **kwargs):
        raise URLError("test")
    monkeypatch.setattr(cps230, "urlopen", fail)
    with pytest.raises(ValueError, match="APRA download failed"):
        cps230.download(source, tmp_path / "raw")


def test_prepare_retains_page_provenance_and_checks_hash(tmp_path, monkeypatch):
    """Verify prepare retains page provenance and checks hash."""
    kit, raw = tmp_path / "kit", tmp_path / "raw"
    (kit / "inputs").mkdir(parents=True)
    raw.mkdir()
    data = b"synthetic PDF placeholder, parsed by a mock"
    (raw / "standard.pdf").write_bytes(data)
    manifest = {"sha256": sha256(data), "edition": "fixture"}
    (raw / "manifest.json").write_text(json.dumps(manifest))
    (kit / "inputs/source.json").write_text(json.dumps(manifest))
    (kit / "inputs/questions.csv").write_text("id,question\nq1,incident notify\n")
    (kit / "prompt.txt").write_text("Cite source pages.")
    monkeypatch.setattr(cps230, "KIT", kit)
    pages = [SimpleNamespace(extract_text=lambda: "synthetic incident notify page")]
    monkeypatch.setattr(cps230, "PdfReader", lambda *a: SimpleNamespace(pages=pages))
    out = tmp_path / "prompts"
    assert cps230.prepare(raw, out, "search") == 1
    record = json.loads((out / "q1.context.json").read_text())
    assert record["pdf_pages"] == [1] and record["source_sha256"] == sha256(data)
    assert record["prompt_sha256"] == sha256((out / "q1.txt").read_bytes())
    (raw / "standard.pdf").write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash"):
        cps230.prepare(raw, tmp_path / "second", "search")
