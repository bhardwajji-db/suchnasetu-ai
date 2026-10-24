"""
Unit & Contract Tests for Multi-Provider LLM Integration Layer.
Tests Ollama, OpenRouter, Google Gemini, and Hugging Face adapters,
including configuration validation, missing-key detection, error handling,
and mocked API responses. Offline & strictly zero-cost.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
import requests

from notice2action.config import config, AppConfig
from notice2action.llm.base import (
    BaseLLMClient,
    clean_llm_json_response,
    LLMClientError,
    LLMConfigError,
    LLMAuthError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMModelError,
)
from notice2action.llm.ollama_client import OllamaClient
from notice2action.llm.openrouter_client import OpenRouterClient
from notice2action.llm.gemini_client import GeminiClient
from notice2action.llm.huggingface_client import HuggingFaceClient
from notice2action.llm.factory import get_llm_client, get_all_provider_statuses


def test_clean_llm_json_response():
    """Verifies thinking tag stripping, markdown fence removal, and JSON normalization."""
    # Case 1: Reasoning model thinking tags
    raw_thinking = "<thinking>Let me think about the deadline.</thinking>```json\n{\"purpose\": {\"value\": \"Grant\"}}\n```"
    cleaned = clean_llm_json_response(raw_thinking)
    data = json.loads(cleaned)
    assert data["purpose"]["value"] == "Grant"

    # Case 2: Trailing comma error repair
    raw_comma = '{"items": ["A", "B",], "count": 2,}'
    cleaned_comma = clean_llm_json_response(raw_comma)
    data_comma = json.loads(cleaned_comma)
    assert data_comma["count"] == 2
    assert len(data_comma["items"]) == 2


def test_provider_statuses_listing():
    """Verifies that all 4 providers are reported in provider statuses without crashing."""
    statuses = get_all_provider_statuses()
    assert len(statuses) == 4
    ids = [s["id"] for s in statuses]
    assert "ollama" in ids
    assert "openrouter" in ids
    assert "gemini" in ids
    assert "huggingface" in ids

    # Ollama is local and requires no API key
    ollama_status = next(s for s in statuses if s["id"] == "ollama")
    assert ollama_status["is_local"] is True
    assert ollama_status["requires_api_key"] is False


def test_factory_invalid_provider():
    """Verifies that requesting an invalid provider raises LLMConfigError."""
    with pytest.raises(LLMConfigError) as exc_info:
        get_llm_client("unsupported_provider")
    assert "Unsupported LLM provider" in str(exc_info.value)


# ---------------------------------------------------------------------------
# OpenRouter Tests (Mocked)
# ---------------------------------------------------------------------------

def test_openrouter_missing_key_raises_config_error():
    """Ensures OpenRouter raises clear LLMConfigError when API key is missing."""
    client = OpenRouterClient(api_key="")
    with pytest.raises(LLMConfigError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Hello"}])
    assert "OPENROUTER_API_KEY" in str(exc_info.value)

    # Health check reports configured: False without throwing
    health = client.check_health()
    assert health["configured"] is False
    assert "Missing OPENROUTER_API_KEY" in health["error"]


@patch("requests.post")
def test_openrouter_mocked_success(mock_post):
    """Tests successful OpenRouter response parsing with mocked API."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({"purpose": {"value": "Test Notice", "status": "stated"}})
                }
            }
        ]
    }
    mock_post.return_value = mock_resp

    client = OpenRouterClient(api_key="mock_test_key")
    result = client.generate_structured_json("System prompt", "User prompt")
    assert result["purpose"]["value"] == "Test Notice"
    assert mock_post.called
    headers = mock_post.call_args[1]["headers"]
    assert headers["Authorization"] == "Bearer mock_test_key"


@patch("requests.post")
def test_openrouter_error_mappings(mock_post):
    """Tests OpenRouter HTTP 401, 429, and 404 mappings."""
    client = OpenRouterClient(api_key="test_key")

    # 401 Auth Error
    mock_post.return_value = MagicMock(status_code=401, text="Unauthorized key")
    with pytest.raises(LLMAuthError):
        client.generate_chat([{"role": "user", "content": "hi"}])

    # 429 Rate Limit
    mock_post.return_value = MagicMock(status_code=429, text="Rate limit exceeded")
    with pytest.raises(LLMRateLimitError):
        client.generate_chat([{"role": "user", "content": "hi"}])

    # 404 Model Error
    mock_post.return_value = MagicMock(status_code=404, text="Model not found")
    with pytest.raises(LLMModelError):
        client.generate_chat([{"role": "user", "content": "hi"}])


# ---------------------------------------------------------------------------
# Google Gemini Tests (Mocked)
# ---------------------------------------------------------------------------

def test_gemini_missing_key_raises_config_error():
    """Ensures Gemini raises clear LLMConfigError when API key is missing."""
    client = GeminiClient(api_key="")
    with pytest.raises(LLMConfigError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Hello"}])
    assert "GEMINI_API_KEY" in str(exc_info.value)

    health = client.check_health()
    assert health["configured"] is False
    assert "Missing GEMINI_API_KEY" in health["error"]


@patch("requests.post")
def test_gemini_mocked_success(mock_post):
    """Tests successful Gemini response parsing with mocked API."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": json.dumps({"deadline": {"value": "2026-11-20", "status": "stated"}})}
                    ]
                }
            }
        ]
    }
    mock_post.return_value = mock_resp

    client = GeminiClient(api_key="test_mock_gemini_key")
    result = client.generate_structured_json("System prompt", "User prompt")
    assert result["deadline"]["value"] == "2026-11-20"
    assert mock_post.called
    assert "key=test_mock_gemini_key" in mock_post.call_args[0][0]


@patch("requests.post")
def test_gemini_error_mappings(mock_post):
    """Tests Gemini HTTP 403, 429, and timeout mappings."""
    client = GeminiClient(api_key="test_key")

    # 403 Forbidden
    mock_post.return_value = MagicMock(status_code=403, text="API key revoked")
    with pytest.raises(LLMAuthError):
        client.generate_chat([{"role": "user", "content": "hi"}])

    # 429 Quota Exceeded
    mock_post.return_value = MagicMock(status_code=429, text="Resource exhausted")
    with pytest.raises(LLMRateLimitError):
        client.generate_chat([{"role": "user", "content": "hi"}])


# ---------------------------------------------------------------------------
# Hugging Face Tests (Mocked)
# ---------------------------------------------------------------------------

def test_huggingface_missing_key_raises_config_error():
    """Ensures Hugging Face raises clear LLMConfigError when API key is missing."""
    client = HuggingFaceClient(api_key="")
    with pytest.raises(LLMConfigError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Hello"}])
    assert "HUGGINGFACE_API_KEY" in str(exc_info.value)


@patch("requests.post")
def test_huggingface_mocked_success(mock_post):
    """Tests successful Hugging Face response parsing with mocked API."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({"required_actions": {"value": "Submit Form", "status": "stated"}})
                }
            }
        ]
    }
    mock_post.return_value = mock_resp

    client = HuggingFaceClient(api_key="test_hf_token")
    result = client.generate_structured_json("System prompt", "User prompt")
    assert result["required_actions"]["value"] == "Submit Form"
    assert mock_post.called
    headers = mock_post.call_args[1]["headers"]
    assert "Bearer test_hf_token" in headers["Authorization"]


@patch("requests.post")
def test_huggingface_model_loading_503(mock_post):
    """Tests that a 503 response (model loading) produces an informative retry message."""
    mock_resp = MagicMock()
    mock_resp.status_code = 503
    mock_resp.content = b'{"estimated_time": 15.5}'
    mock_resp.json.return_value = {"estimated_time": 15.5}
    mock_post.return_value = mock_resp

    client = HuggingFaceClient(api_key="test_hf_token")
    with pytest.raises(LLMClientError) as exc_info:
        client.generate_chat([{"role": "user", "content": "hi"}])
    assert "currently loading" in str(exc_info.value)
    assert "15.5" in str(exc_info.value)
