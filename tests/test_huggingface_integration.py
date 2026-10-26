"""
Comprehensive Unit & Integration Test Suite for Hugging Face Gemma 4 Provider.
Tests environment configuration, token handling, error taxonomy, retry logic,
NoticeAnalyzer integration, FollowUpAssistant Q&A, and token sanitization.
All external network calls are strictly mocked in automated test runs.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
import requests

from notice2action.config import AppConfig
from notice2action.llm.base import (
    LLMAuthError,
    LLMClientError,
    LLMConfigError,
    LLMConnectionError,
    LLMModelError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from notice2action.llm.factory import get_all_provider_statuses, get_llm_client
from notice2action.llm.huggingface_client import (
    HuggingFaceClient,
    _sanitize_error_text,
)
from notice2action.analysis import NoticeAnalyzer
from notice2action.followup import FollowUpAssistant


# ---------------------------------------------------------------------------
# 1. Configuration & Provider Discovery Tests
# ---------------------------------------------------------------------------

def test_huggingface_config_env_vars(monkeypatch):
    """Verifies HF_TOKEN, AI_PROVIDER, and HF_MODEL_ID resolve correctly."""
    monkeypatch.setenv("AI_PROVIDER", "huggingface")
    monkeypatch.setenv("HF_TOKEN", "hf_mock_token_for_config_test_12345")
    monkeypatch.setenv("HF_MODEL_ID", "google/gemma-4-26B-A4B")
    monkeypatch.setenv("HF_PROVIDER", "featherless-ai")

    cfg = AppConfig()
    assert cfg.llm_provider == "huggingface"
    assert cfg.hf_token == "hf_mock_token_for_config_test_12345"
    assert cfg.huggingface_api_key == "hf_mock_token_for_config_test_12345"
    assert cfg.huggingface_model == "google/gemma-4-26B-A4B"
    assert cfg.hf_provider == "featherless-ai"


def test_huggingface_provider_factory_and_statuses(monkeypatch):
    """Verifies factory instantiates HuggingFaceClient and status reports correctly."""
    monkeypatch.setenv("HF_TOKEN", "hf_mock_token_status_test")
    monkeypatch.setenv("HF_MODEL_ID", "google/gemma-4-26B-A4B")

    client = get_llm_client("huggingface")
    assert isinstance(client, HuggingFaceClient)
    assert client.provider_name == "huggingface"
    assert client.model == "google/gemma-4-26B-A4B"

    statuses = get_all_provider_statuses()
    hf_status = next((s for s in statuses if s["id"] == "huggingface"), None)
    assert hf_status is not None
    assert hf_status["model"] == "google/gemma-4-26B-A4B"
    assert hf_status["key_configured"] is True


# ---------------------------------------------------------------------------
# 2. Token Handling & Sanitization Tests
# ---------------------------------------------------------------------------

def test_token_sanitization_removes_secrets():
    """Verifies that error messages strip real or synthetic Hugging Face tokens."""
    token = "hf_SecretLiveTokenExample123456789"
    raw_error = f"HTTP 401 Unauthorized for Bearer {token}: Invalid authorization header."
    sanitized = _sanitize_error_text(raw_error, token=token)

    assert token not in sanitized
    assert "Bearer [REDACTED_TOKEN]" in sanitized or "[REDACTED_HF_TOKEN]" in sanitized


def test_missing_token_raises_config_error():
    """Verifies that an unconfigured HuggingFaceClient raises LLMConfigError."""
    client = HuggingFaceClient(api_key="")
    health = client.check_health()
    assert health["configured"] is False
    assert health["connected"] is False
    assert "Missing HF_TOKEN" in health["error"]

    with pytest.raises(LLMConfigError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Hello"}])
    assert "HF_TOKEN" in str(exc_info.value)
    assert "HUGGINGFACE_API_KEY" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 3. Error Taxonomy Mapping (Mocked External Calls)
# ---------------------------------------------------------------------------

@patch("requests.post")
def test_auth_error_mapping(mock_post):
    """Verifies HTTP 401/403 maps to LLMAuthError without leaking credentials."""
    client = HuggingFaceClient(api_key="hf_dummy_test_token_abc")

    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = "Unauthorized"
    mock_post.return_value = mock_resp

    with pytest.raises(LLMAuthError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Test"}])
    assert "401" in str(exc_info.value)
    assert "hf_dummy_test_token_abc" not in str(exc_info.value)


@patch("requests.post")
def test_rate_limit_error_mapping(mock_post):
    """Verifies HTTP 429 maps to LLMRateLimitError."""
    client = HuggingFaceClient(api_key="hf_dummy_test_token_abc")

    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.text = "Too Many Requests: Rate limit exceeded"
    mock_post.return_value = mock_resp

    with pytest.raises(LLMRateLimitError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Test"}])
    assert "rate limit" in str(exc_info.value).lower()


@patch("requests.post")
def test_timeout_error_mapping(mock_post):
    """Verifies inference timeout maps to LLMTimeoutError."""
    client = HuggingFaceClient(api_key="hf_dummy_test_token_abc", timeout_seconds=5)
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out after 5s")

    with pytest.raises(LLMTimeoutError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Test"}])
    assert "timed out" in str(exc_info.value).lower()


@patch("requests.post")
def test_model_not_found_mapping(mock_post):
    """Verifies HTTP 404 maps to LLMModelError."""
    client = HuggingFaceClient(api_key="hf_dummy_test_token_abc", model="google/non-existent-model")

    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Model not found on Hugging Face"
    mock_post.return_value = mock_resp

    with pytest.raises(LLMModelError) as exc_info:
        client.generate_chat([{"role": "user", "content": "Test"}])
    assert "not found" in str(exc_info.value).lower()


@patch("requests.post")
def test_transient_loading_retry_success(mock_post):
    """Verifies that transient 503 model-loading error is retried and succeeds on attempt 2."""
    client = HuggingFaceClient(api_key="hf_dummy_test_token_abc")

    mock_resp_503 = MagicMock()
    mock_resp_503.status_code = 503
    mock_resp_503.content = b'{"estimated_time": 15.5}'
    mock_resp_503.json.return_value = {"estimated_time": 15.5}

    mock_success = MagicMock()
    mock_success.status_code = 200
    mock_success.json.return_value = {
        "choices": [{"message": {"content": "Success from Gemma 4 after warmup!"}}]
    }

    mock_post.side_effect = [mock_resp_503, mock_success]

    with patch("time.sleep") as mock_sleep:
        res = client.generate_chat([{"role": "user", "content": "Ping"}])
        assert res == "Success from Gemma 4 after warmup!"
        assert mock_sleep.called
        assert mock_post.call_count == 2


# ---------------------------------------------------------------------------
# 4. End-to-End Notice Analysis & Evidence Grounding Integration
# ---------------------------------------------------------------------------

@patch("requests.post")
def test_notice_analyzer_with_huggingface_client(mock_post):
    """Verifies full NoticeAnalyzer pipeline with HuggingFaceClient using mocked model output."""
    sample_structured_response = json.dumps({
        "issuing_authority": {
            "value": "National Testing Agency",
            "evidence_quote": "National Testing Agency",
            "status": "VERIFIED",
        },
        "notice_reference_number": {
            "value": "NTA/2026/01",
            "evidence_quote": "NTA/2026/01",
            "status": "VERIFIED",
        },
        "notice_date": {
            "value": "2026-10-20",
            "evidence_quote": "20 October 2026",
            "status": "VERIFIED",
        },
        "recipient": {
            "value": "All eligible candidates",
            "evidence_quote": "All eligible candidates",
            "status": "VERIFIED",
        },
        "main_subject": {
            "value": "UGC NET December 2026 Examination Notice",
            "evidence_quote": "UGC NET December 2026",
            "status": "VERIFIED",
        },
        "required_action_and_deadline": {
            "value": "Submit online form by 25 November 2026",
            "evidence_quote": "Last date for submission of online application form is 25 November 2026.",
            "status": "VERIFIED",
        },
        "purpose": {
            "value": "UGC NET Examination cycle",
            "evidence_quote": "UGC NET December 2026",
            "status": "VERIFIED",
        },
        "eligibility": {
            "value": "Master degree with at least 55% marks",
            "evidence_quote": "Master degree with at least 55% marks for General category.",
            "status": "VERIFIED",
        },
        "deadline": {
            "value": "2026-11-25",
            "evidence_quote": "25 November 2026",
            "status": "VERIFIED",
        },
        "fee_or_cost": {
            "value": "Not Stated",
            "evidence_quote": "",
            "status": "NOT_STATED",
        },
        "required_documents": {
            "value": "Master degree certificates",
            "evidence_quote": "",
            "status": "NOT_STATED",
        },
        "contact_details": {
            "value": "nta.ac.in",
            "evidence_quote": "",
            "status": "NOT_STATED",
        },
        "required_actions": {
            "value": "Submit application online",
            "evidence_quote": "submission of online application form",
            "status": "VERIFIED",
        },
        "important_conditions": {
            "value": "Minimum 55% marks required",
            "evidence_quote": "at least 55% marks",
            "status": "VERIFIED",
        },
        "missing_information": [],
        "uncertain_or_conflicting_details": [],
    })

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": f"```json\n{sample_structured_response}\n```"}}]
    }
    mock_post.return_value = mock_resp

    client = HuggingFaceClient(api_key="hf_mock_integration_key")

    notice_text = (
        "National Testing Agency. UGC NET December 2026. Ref NTA/2026/01. "
        "Dated 20 October 2026. All eligible candidates. "
        "Last date for submission of online application form is 25 November 2026. "
        "Master degree with at least 55% marks for General category."
    )

    analyzer = NoticeAnalyzer(client=client)
    result = analyzer.analyze_notice(notice_text)

    assert result.issuing_authority.value == "National Testing Agency"
    assert result.deadline.value == "2026-11-25"
    assert "55%" in result.eligibility.value
    assert result.deadline.evidence_quote == "25 November 2026"


@patch("requests.post")
def test_followup_qa_with_huggingface_client(mock_post):
    """Verifies FollowUpAssistant question-answering with HuggingFaceClient."""
    sample_qa_response = json.dumps({
        "question": "What is the fee for General category?",
        "answer": "The application fee for General category is Rs 1150.",
        "is_supported": True,
        "evidence_quote": "Application fee for General category is Rs 1150.",
        "unsupported_message": None,
    })

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": sample_qa_response}}]
    }
    mock_post.return_value = mock_resp

    client = HuggingFaceClient(api_key="hf_mock_integration_key")
    notice_context = "Official Notice. Application fee for General category is Rs 1150. Submit before deadline."

    assistant = FollowUpAssistant(client=client)
    qa_result = assistant.answer_question(
        question="What is the fee for General category?",
        raw_notice_text=notice_context,
        target_lang="en",
    )

    assert "1150" in qa_result.answer
    assert qa_result.is_supported is True
    assert qa_result.evidence_quote == "Application fee for General category is Rs 1150."


# ---------------------------------------------------------------------------
# 5. FastAPI Provider Selection & Health Routes
# ---------------------------------------------------------------------------

def test_api_providers_list(monkeypatch):
    """Verifies GET /api/providers returns Hugging Face in the list."""
    monkeypatch.setenv("HF_MODEL_ID", "google/gemma-4-26B-A4B")
    from starlette.testclient import TestClient
    from notice2action.api.server import app

    client = TestClient(app)
    response = client.get("/api/providers")
    assert response.status_code == 200
    providers = response.json()
    hf = next((p for p in providers if p["id"] == "huggingface"), None)
    assert hf is not None
    assert hf["model"] == "google/gemma-4-26B-A4B"


def test_api_providers_select_huggingface(monkeypatch):
    """Verifies POST /api/providers/select can switch to huggingface safely."""
    from starlette.testclient import TestClient
    from notice2action.api.server import app

    client = TestClient(app)
    try:
        response = client.post("/api/providers/select", json={"provider": "huggingface"})
        assert response.status_code == 200
        data = response.json()
        assert data["active_provider"] == "huggingface"
        assert data["status"]["provider"] == "huggingface"
    finally:
        client.post("/api/providers/select", json={"provider": "ollama"})
