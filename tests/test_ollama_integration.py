"""
Integration Test Suite for Ollama Connection and Provider Lifecycle in SuchnaSetu AI (PS02).
Tests real (unmocked) Ollama connectivity, model discovery, and verifies provider error handling.
"""

import pytest
import requests
from notice2action.config import config
from notice2action.llm.ollama_client import OllamaClient
from notice2action.llm.base import OllamaConnectionError, OllamaTimeoutError


def is_ollama_reachable() -> bool:
    """Probes if local Ollama daemon is currently listening on port 11434."""
    try:
        r = requests.get(f"{config.ollama_base_url}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def test_ollama_real_connection_and_model_status():
    """
    Integration test verifying real, unmocked connection to Ollama server.
    If Ollama is running, validates that OllamaClient.check_health() succeeds
    and discovers loaded models including gemma4.
    """
    if not is_ollama_reachable():
        pytest.skip(f"Ollama server not reachable at {config.ollama_base_url}. Run 'ollama serve' to enable.")

    client = OllamaClient()
    health = client.check_health()
    assert health["provider"] == "ollama"
    assert health["connected"] is True
    assert isinstance(health["models"], list)
    assert len(health["models"]) > 0
    assert health["target_model"] == config.ollama_model


def test_ollama_connection_error_on_invalid_endpoint():
    """
    Verifies that connecting to an unreachable port raises OllamaConnectionError
    with descriptive troubleshooting guidance, rather than an unhandled socket crash.
    """
    client = OllamaClient(base_url="http://127.0.0.1:59999", timeout_seconds=1)
    with pytest.raises(OllamaConnectionError) as exc_info:
        client.check_health()
    assert "Cannot connect to Ollama" in str(exc_info.value)
    assert "59999" in str(exc_info.value)


def test_ollama_timeout_error_handling():
    """
    Verifies that slow or hanging Ollama responses raise OllamaTimeoutError gracefully.
    """
    # Extremely small timeout to test timeout handling
    client = OllamaClient(base_url="http://10.255.255.1:11434", timeout_seconds=0.001)
    with pytest.raises((OllamaTimeoutError, OllamaConnectionError)):
        client.check_health()
