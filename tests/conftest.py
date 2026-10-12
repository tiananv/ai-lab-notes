"""Keep every test offline and temporary test files inside the repository cache."""

import socket

import pytest


@pytest.fixture(autouse=True)
def no_live_network(monkeypatch):
    """Fail any test that tries to open a real network connection."""
    def blocked(*args, **kwargs):
        raise AssertionError("Tests must mock all network access")
    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


@pytest.fixture(autouse=True)
def no_real_keys(monkeypatch):
    """Remove model credentials from the test process without reading their values."""
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY", "LLM_MODEL"):
        monkeypatch.delenv(name, raising=False)
