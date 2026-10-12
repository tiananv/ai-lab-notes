"""Mock all model backends and check provenance, failures and manual resumption."""

import io
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from urllib.error import HTTPError, URLError

import pytest

from scripts import llm
from scripts.common import cli

ANSWER = Path("tests/fixtures/responses/manual.txt")


def test_manual_prepare_and_import_keep_exact_prompt(tmp_path):
    """Verify manual prepare and import keep exact prompt."""
    prompt = "Synthetic prompt\r\nwith exact newlines."
    meta = llm.run(prompt, tmp_path, "manual", "mock-model")
    assert meta["status"] == "awaiting-answer"
    assert not (tmp_path / "output.txt").exists()
    assert (tmp_path / "prompt.txt").read_bytes() == prompt.encode()
    assert meta["prompt_sha256"] == llm.sha256(prompt.encode())
    assert meta["timestamp_utc"].endswith("+00:00")
    finished = llm.run(prompt, tmp_path, "manual", "mock-model", ANSWER)
    assert finished["status"] == "complete"
    assert finished["duration_seconds"] is None
    assert finished["output_sha256"] == llm.sha256(ANSWER.read_bytes())
    with pytest.raises(llm.ModelError, match="already has an output"):
        llm.run(prompt, tmp_path, "manual", "mock-model", ANSWER)


def test_changed_prompt_or_model_cannot_resume(tmp_path):
    """Verify changed prompt or model cannot resume."""
    llm.run("one", tmp_path, "manual", "mock")
    with pytest.raises(llm.ModelError, match="settings changed"):
        llm.run("two", tmp_path, "manual", "mock", ANSWER)
    with pytest.raises(llm.ModelError, match="settings changed"):
        llm.run("one", tmp_path, "manual", "different", ANSWER)


def test_empty_answer_never_completes(tmp_path):
    """Verify empty answer never completes."""
    empty = tmp_path / "empty.txt"
    empty.write_text(" ")
    out = tmp_path / "trial"
    with pytest.raises(llm.ModelError, match="empty"):
        llm.run("prompt", out, "manual", "mock", empty)
    assert json.loads((out / "metadata.json").read_text())["status"] == "error"
    assert not (out / "output.txt").exists()


@pytest.mark.parametrize("backend", ["anthropic", "openai", "openrouter"])
def test_missing_keys_are_friendly_and_do_not_call_network(tmp_path, backend, capsys):
    """Verify missing keys are friendly and do not call network."""
    with pytest.raises(SystemExit) as stopped:
        cli(lambda: llm.run("prompt", tmp_path, backend, "mock"))
    assert stopped.value.code == 2
    text = capsys.readouterr().out
    assert llm.KEYS[backend] in text and "Traceback" not in text
    assert json.loads((tmp_path / "metadata.json").read_text())["status"] == "error"


@pytest.mark.parametrize("backend", ["anthropic", "openai", "openrouter", "ollama"])
def test_http_backends_use_expected_protocol_and_record_model(tmp_path, monkeypatch, backend):
    """Verify http backends use expected protocol and record model."""
    seen = []
    if backend in llm.KEYS:
        monkeypatch.setenv(llm.KEYS[backend], "synthetic-test-key")
    response = {"model": "mock-resolved", "content": [{"type": "text", "text": "mock answer"}],
                "response": "mock answer", "done": True, "done_reason": "stop",
                "choices": [{"message": {"content": "mock answer"}, "finish_reason": "stop"}],
                "stop_reason": "end_turn"}
    def fake_open(request, timeout):
        seen.append((request, json.loads(request.data), timeout))
        return io.BytesIO(json.dumps(response).encode())
    monkeypatch.setattr(llm, "urlopen", fake_open)
    meta = llm.run("exact prompt", tmp_path, backend, "mock-requested")
    request, payload, timeout = seen[0]
    assert request.full_url == llm.URLS[backend] and timeout == 120
    assert payload["model"] == "mock-requested"
    if backend == "ollama":
        assert payload["prompt"] == "exact prompt" and payload["stream"] is False
    else:
        assert payload["messages"] == [{"role": "user", "content": "exact prompt"}]
    if backend == "anthropic":
        assert request.get_header("X-api-key") == "synthetic-test-key"
    elif backend != "ollama":
        assert request.get_header("Authorization") == "Bearer synthetic-test-key"
    assert meta["model_id"] == "mock-resolved" and meta["status"] == "complete"
    assert "synthetic-test-key" not in (tmp_path / "metadata.json").read_text()


def test_claude_cli_is_mocked_and_uses_stdin_without_shell(tmp_path, monkeypatch):
    """Verify claude cli is mocked and uses stdin without shell."""
    def fake_run(command, **kwargs):
        assert command[:2] == ["claude", "-p"]
        assert "--no-session-persistence" in command and "--strict-mcp-config" in command
        assert command[command.index("--tools") + 1] == ""
        assert kwargs["input"] == "prompt" and "shell" not in kwargs
        return SimpleNamespace(stdout=json.dumps({"result": "synthetic answer", "is_error": False}))
    monkeypatch.setattr(llm.subprocess, "run", fake_run)
    assert llm.run("prompt", tmp_path, "claude-cli", "mock")["status"] == "complete"


@pytest.mark.parametrize("failure", [FileNotFoundError(), subprocess.TimeoutExpired("claude", 180),
                                     subprocess.CalledProcessError(1, "claude")])
def test_cli_failures_are_friendly(tmp_path, monkeypatch, failure):
    """Verify cli failures are friendly."""
    def fail(*args, **kwargs):
        raise failure
    monkeypatch.setattr(llm.subprocess, "run", fail)
    with pytest.raises(llm.ModelError):
        llm.run("prompt", tmp_path, "claude-cli", "mock")
    assert not (tmp_path / "output.txt").exists()


@pytest.mark.parametrize("failure", [URLError("private detail"), TimeoutError(),
    HTTPError("url", 401, "private detail", None, io.BytesIO(b"private body"))])
def test_transport_errors_do_not_echo_provider_bodies(tmp_path, monkeypatch, failure):
    """Verify transport errors do not echo provider bodies."""
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")
    def fail(*args, **kwargs):
        raise failure
    monkeypatch.setattr(llm, "urlopen", fail)
    with pytest.raises(llm.ModelError) as error:
        llm.run("prompt", tmp_path, "openai", "mock")
    assert "private" not in str(error.value) and "synthetic-test-key" not in str(error.value)


@pytest.mark.parametrize("response", [{}, {"choices": []}, {"error": "private error"},
    {"choices": [{"message": {"content": None}}]}])
def test_bad_provider_responses_cannot_be_results(tmp_path, monkeypatch, response):
    """Verify bad provider responses cannot be results."""
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-test-key")
    monkeypatch.setattr(llm, "urlopen", lambda *a, **k: io.BytesIO(json.dumps(response).encode()))
    with pytest.raises(llm.ModelError):
        llm.run("prompt", tmp_path, "openai", "mock")
    assert not (tmp_path / "output.txt").exists()


def test_cloud_tag_is_rejected_for_local_kit(tmp_path):
    """Verify cloud tag is rejected for local kit."""
    with pytest.raises(llm.ModelError, match="local model"):
        llm.run("prompt", tmp_path, "ollama", "mock-cloud")


def test_compose_prompt_keeps_exact_input_bytes(tmp_path):
    """Verify compose prompt keeps exact input bytes."""
    source = tmp_path / "input.txt"
    source.write_bytes(b"A\r\nB")
    result = llm.compose_prompt(ANSWER, [source])
    assert result.endswith("A\r\nB") and "--- Input: input.txt ---" in result


def test_model_choice_required(tmp_path):
    """Verify model choice required."""
    with pytest.raises(llm.ModelError, match="Choose --model"):
        llm.run("prompt", tmp_path, "manual", "")
