"""Run a text prompt through one backend and retain an auditable local record."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.common import cli, write_json

BACKENDS = ("manual", "claude-cli", "anthropic", "openai", "openrouter", "ollama")
KEYS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY"}
URLS = {"anthropic": "https://api.anthropic.com/v1/messages",
        "openai": "https://api.openai.com/v1/chat/completions",
        "openrouter": "https://openrouter.ai/api/v1/chat/completions",
        "ollama": "http://127.0.0.1:11434/api/generate"}


class ModelError(ValueError):
    """An actionable model failure safe to show without provider response bodies."""


def sha256(data: bytes) -> str:
    """Return the SHA-256 fingerprint of exact bytes."""
    return hashlib.sha256(data).hexdigest()


def compose_prompt(prompt: Path, inputs: list[Path]) -> str:
    """Append labelled input files to the instructions in a stable order."""
    text = prompt.read_bytes().decode("utf-8")
    for path in inputs:
        text += f"\n\n--- Input: {path.name} ---\n" + path.read_bytes().decode("utf-8")
    if not text.strip():
        raise ModelError("The prompt is empty")
    return text


def _post(url: str, payload: dict, headers: dict) -> dict:
    request = Request(url, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json", **headers}, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            result = json.load(response)
    except HTTPError as error:
        raise ModelError(f"Provider returned HTTP {error.code}. Check model access, key and quota.") from None
    except (URLError, TimeoutError, OSError):
        raise ModelError("Cannot reach the model. Check the connection or local Ollama server.") from None
    except (ValueError, UnicodeError):
        raise ModelError("Provider returned unreadable JSON; no answer was recorded.") from None
    if not isinstance(result, dict) or result.get("error"):
        raise ModelError("Provider reported an error; no answer was recorded.")
    return result


def _call(prompt: str, backend: str, model: str) -> tuple[str, str, dict]:
    if backend == "claude-cli":
        try:
            completed = subprocess.run(
                ["claude", "-p", "--model", model, "--output-format", "json", "--tools", "",
                 "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
                 "--no-session-persistence"], input=prompt, text=True, capture_output=True,
                timeout=180, check=True,
            )
            result = json.loads(completed.stdout)
        except FileNotFoundError:
            raise ModelError("Install Claude Code and sign in, or use --backend manual.") from None
        except (subprocess.SubprocessError, ValueError):
            raise ModelError("Claude Code failed. Check its sign-in and selected model.") from None
        if not isinstance(result, dict) or result.get("is_error"):
            raise ModelError("Claude Code returned an error; no answer was recorded.")
        return result.get("result", ""), model, {"tools": "disabled"}
    headers = {}
    if backend in KEYS:
        key = os.environ.get(KEYS[backend], "").strip()
        if not key:
            raise ModelError(f"Set {KEYS[backend]} locally, or use --backend manual.")
        headers = {"Authorization": f"Bearer {key}"}
    messages = [{"role": "user", "content": prompt}]
    if backend == "anthropic":
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        settings = {"max_tokens": 4096}
        payload = {"model": model, "messages": messages, **settings}
    elif backend == "ollama":
        if "cloud" in model.lower():
            raise ModelError("Use a downloaded local model, not a cloud model, for this kit.")
        settings = {"stream": False, "options": {"num_predict": 4096, "num_ctx": 32768}}
        payload = {"model": model, "prompt": prompt, **settings}
    else:
        settings = {("max_completion_tokens" if backend == "openai" else "max_tokens"): 4096}
        payload = {"model": model, "messages": messages, **settings}
    result = _post(URLS[backend], payload, headers)
    try:
        if backend == "anthropic":
            answer = "\n".join(part["text"] for part in result["content"] if part["type"] == "text")
            stop = result.get("stop_reason")
        elif backend == "ollama":
            answer, stop = result["response"], result.get("done_reason")
            if result.get("done") is not True:
                raise ModelError("Ollama did not complete its response.")
        else:
            answer = result["choices"][0]["message"]["content"]
            stop = result["choices"][0].get("finish_reason")
    except (KeyError, IndexError, TypeError):
        raise ModelError("Provider response has no usable text answer.") from None
    return answer, result.get("model", model), {**settings, "stop_reason": stop}


def run(prompt: str, output_dir: Path, backend: str, model: str,
        answer_file: Path | None = None) -> dict:
    """Prepare or complete a single trial, refusing to overwrite a finished run."""
    if backend not in BACKENDS:
        raise ModelError(f"Choose a backend from {', '.join(BACKENDS)}")
    if not model or not model.strip():
        raise ModelError("Choose --model or set LLM_MODEL; record the exact model shown by your tool.")
    if not prompt.strip():
        raise ModelError("The prompt is empty")
    if answer_file and backend != "manual":
        raise ModelError("--answer is only used with --backend manual")
    prompt_bytes = prompt.encode("utf-8")
    fingerprint = sha256(prompt_bytes)
    meta_path = output_dir / "metadata.json"
    if (output_dir / "output.txt").exists():
        raise ModelError("This run already has an output. Choose a fresh --out directory.")
    if meta_path.exists():
        old = json.loads(meta_path.read_text(encoding="utf-8"))
        if (old.get("prompt_sha256"), old.get("backend"), old.get("requested_model")) != (
            fingerprint, backend, model
        ):
            raise ModelError("Run settings changed. Choose a fresh --out directory.")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "prompt.txt").write_bytes(prompt_bytes)
    meta = {"backend": backend, "requested_model": model, "model_id": model,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(), "prompt_sha256": fingerprint,
            "status": "awaiting-answer" if backend == "manual" else "running",
            "duration_seconds": None, "output_sha256": None}
    write_json(meta_path, meta)
    if backend == "manual" and answer_file is None:
        return meta
    start = time.monotonic()
    try:
        if backend == "manual":
            answer = answer_file.read_bytes().decode("utf-8")
            settings = {"capture": "manual; model identity is user recorded"}
        else:
            answer, meta["model_id"], settings = _call(prompt, backend, model)
            meta["duration_seconds"] = round(time.monotonic() - start, 3)
        if not isinstance(answer, str) or not answer.strip():
            raise ModelError("The answer is empty; no completed result was recorded.")
        output = answer.encode("utf-8")
        (output_dir / "output.txt").write_bytes(output)
        meta.update(status="complete", output_sha256=sha256(output), settings=settings)
    except (ModelError, OSError, UnicodeError):
        meta["status"] = "error"
        write_json(meta_path, meta)
        raise
    write_json(meta_path, meta)
    return meta


def main() -> None:
    """Send a prompt or import an actual manually obtained answer."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--input", action="append", type=Path, default=[])
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--backend", choices=BACKENDS, default=os.getenv("LLM_BACKEND", "manual"))
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", ""))
    parser.add_argument("--answer", type=Path)
    args = parser.parse_args()
    meta = run(compose_prompt(args.prompt, args.input), args.out, args.backend, args.model, args.answer)
    print(f'{meta["status"]}: {args.out}')
    if meta["status"] == "awaiting-answer":
        print("Paste prompt.txt into your chosen tool. Save its actual answer elsewhere, then")
        print("repeat this command with --answer PATH_TO_ANSWER. Do not edit prompt.txt.")


if __name__ == "__main__":
    cli(main)
