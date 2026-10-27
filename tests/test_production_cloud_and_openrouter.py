"""
Production Cloud Deployment, OpenRouter Integration, and Infrastructure Tests.
Verifies OpenRouter adapter, cloud compatibility, health endpoints, and database path configurability.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fastapi.testclient import TestClient

from notice2action.config import config, AppConfig
from notice2action.llm.openrouter_client import (
    OpenRouterClient,
    OPENROUTER_API_URL,
    OPENROUTER_AUTH_URL,
    DEFAULT_OPENROUTER_MODEL,
)
from notice2action.llm.base import (
    LLMConfigError,
    LLMAuthError,
    LLMRateLimitError,
    LLMModelError,
    LLMConnectionError,
    LLMTimeoutError,
    LLMClientError,
)
from notice2action.api.server import app


@pytest.fixture
def client():
    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. OpenRouter Configuration & Credentials Tests
# -----------------------------------------------------------------------------

def test_openrouter_defaults_and_env_loading(monkeypatch):
    """Verifies that OpenRouterClient reads OPENROUTER_API_KEY and OPENROUTER_MODEL from env."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-v1-mock-test-key-12345")
    monkeypatch.setenv("OPENROUTER_MODEL", "google/gemma-4-26b-a4b-it:free")
    monkeypatch.setenv("OPENROUTER_MAX_TOKENS", "2048")
    monkeypatch.setenv("OPENROUTER_TIMEOUT_SECONDS", "45")

    client = OpenRouterClient()
    assert client.provider_name == "openrouter"
    assert client.model == "google/gemma-4-26b-a4b-it:free"
    assert client.max_tokens == 2048
    assert client.timeout == 45
    assert client._api_key == "sk-or-v1-mock-test-key-12345"


def test_openrouter_missing_key_raises_config_error(monkeypatch):
    """Verifies clear error when no key is provided, never contacting network."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    client = OpenRouterClient(api_key="")
    with pytest.raises(LLMConfigError) as exc_info:
        client.generate_chat([{"role": "user", "content": "hello"}])
    assert "OPENROUTER_API_KEY" in str(exc_info.value)

    # Health check reports missing key without exception
    health = client.check_health()
    assert health["connected"] is False
    assert health["configured"] is False
    assert "Missing OPENROUTER_API_KEY" in health["error"]


# -----------------------------------------------------------------------------
# 2. OpenRouter Safe Error Handling & Key Redaction
# -----------------------------------------------------------------------------

@patch("requests.post")
def test_openrouter_auth_error_no_key_leakage(mock_post):
    """Ensures 401 raises LLMAuthError without leaking sensitive key in error message."""
    mock_resp = MagicMock()
    mock_resp.status_code = 401
    mock_resp.text = '{"error": {"message": "Invalid API key provided: sk-or-secret-token"}}'
    mock_post.return_value = mock_resp

    client = OpenRouterClient(api_key="sk-or-secret-token")
    with pytest.raises(LLMAuthError) as exc_info:
        client.generate_chat([{"role": "user", "content": "analyze"}])
    
    err_str = str(exc_info.value)
    assert "sk-or-secret-token" not in err_str
    assert "401" in err_str


@patch("requests.post")
def test_openrouter_rate_limit_and_model_error_mapping(mock_post):
    """Ensures 429 maps to LLMRateLimitError and 404 maps to LLMModelError."""
    client = OpenRouterClient(api_key="test_key")

    # Rate limit 429
    mock_429 = MagicMock()
    mock_429.status_code = 429
    mock_429.text = "Rate limit exceeded"
    mock_post.return_value = mock_429
    with pytest.raises(LLMRateLimitError):
        client.generate_chat([{"role": "user", "content": "ping"}])

    # Model not found 404
    mock_404 = MagicMock()
    mock_404.status_code = 404
    mock_404.text = "Model not found"
    mock_post.return_value = mock_404
    with pytest.raises(LLMModelError):
        client.generate_chat([{"role": "user", "content": "ping"}])

    # Insufficient balance 402
    mock_402 = MagicMock()
    mock_402.status_code = 402
    mock_402.text = "Insufficient credits"
    mock_post.return_value = mock_402
    with pytest.raises(LLMAuthError) as exc_402:
        client.generate_chat([{"role": "user", "content": "ping"}])
    assert "balance" in str(exc_402.value).lower()


@patch("requests.post")
def test_openrouter_response_format_retry_resilience(mock_post):
    """
    If OpenRouter model rejects response_format={"type": "json_object"} with HTTP 400,
    the client safely retries without response_format and extracts the JSON response.
    """
    fail_400 = MagicMock()
    fail_400.status_code = 400
    fail_400.text = '{"error": {"message": "Provider does not support response_format json_object"}}'

    success_200 = MagicMock()
    success_200.status_code = 200
    success_200.json.return_value = {
        "choices": [{"message": {"content": '{"authority": "Ministry of Jal Shakti"}'}}]
    }

    mock_post.side_effect = [fail_400, success_200]

    client = OpenRouterClient(api_key="test_key")
    res = client.generate_chat([{"role": "user", "content": "extract"}], json_mode=True)
    assert 'Ministry of Jal Shakti' in res
    assert mock_post.call_count == 2
    # Second call payload should not have response_format
    second_call_payload = mock_post.call_args_list[1][1]["json"]
    assert "response_format" not in second_call_payload


# -----------------------------------------------------------------------------
# 3. Cloud Provider Isolation (No Ollama Requirement)
# -----------------------------------------------------------------------------

def test_cloud_provider_endpoints_bypass_ollama(client, monkeypatch):
    """In openrouter mode, model lifecycle endpoints return cloud status without calling Ollama."""
    monkeypatch.setattr(config, "llm_provider", "openrouter")
    monkeypatch.setattr(config, "openrouter_model", "google/gemma-4-26b-a4b-it:free")

    # Status endpoint
    status_res = client.get("/api/models/status")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["provider"] == "openrouter"
    assert status_data["is_cloud"] is True
    assert status_data["target_model"] == "google/gemma-4-26b-a4b-it:free"

    # Warmup endpoint
    warmup_res = client.post("/api/models/warmup")
    assert warmup_res.status_code == 200
    assert "cloud-hosted" in warmup_res.json()["message"]

    # Unload endpoint
    unload_res = client.post("/api/models/unload")
    assert unload_res.status_code == 200
    assert "cloud-hosted" in unload_res.json()["message"]

    # Unload ollama endpoint
    unload_ol_res = client.post("/api/ollama/unload")
    assert unload_ol_res.status_code == 200
    assert "cloud-hosted" in unload_ol_res.json()["message"]


# -----------------------------------------------------------------------------
# 4. Health Check Endpoints
# -----------------------------------------------------------------------------

def test_root_health_and_healthz_endpoints(client):
    """Verifies that /health and /healthz return 200 OK for Render and container orchestrators."""
    for path in ["/health", "/healthz"]:
        res = client.get(path)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "SuchnaSetu AI" in data["app"]


# -----------------------------------------------------------------------------
# 5. Database Path Configuration & Persistent Disk Support
# -----------------------------------------------------------------------------

def test_database_path_configurable_via_env(monkeypatch, tmp_path):
    """Verifies that DATABASE_PATH and UPLOADS_DIR honor environment variables for persistent disks."""
    custom_db = tmp_path / "custom_data" / "suchnasetu_cloud.db"
    custom_uploads = tmp_path / "custom_data" / "uploads"
    monkeypatch.setenv("DATABASE_PATH", str(custom_db))
    monkeypatch.setenv("UPLOADS_DIR", str(custom_uploads))

    from notice2action.storage.db import DatabaseManager
    db_mgr = DatabaseManager(db_path=custom_db, uploads_dir=custom_uploads)
    assert db_mgr.db_path == custom_db
    assert db_mgr.uploads_dir == custom_uploads
    assert custom_db.parent.is_dir()
    assert custom_uploads.is_dir()

    # Connection operates cleanly on the custom path
    conn = db_mgr.get_connection()
    row = conn.execute("SELECT 1 as num;").fetchone()
    assert row["num"] == 1


# -----------------------------------------------------------------------------
# 6. Cloudflare Pages SPA Routing
# -----------------------------------------------------------------------------

def test_cloudflare_pages_redirects_file():
    """Verifies that frontend/public/_redirects exists and defines SPA wildcard routing."""
    redirects_file = Path("frontend/public/_redirects")
    assert redirects_file.is_file(), "frontend/public/_redirects must exist for Cloudflare Pages"
    content = redirects_file.read_text(encoding="utf-8").strip()
    assert "/*" in content
    assert "/index.html" in content
    assert "200" in content


# -----------------------------------------------------------------------------
# 7. End-to-End Notice Analysis with Mocked OpenRouter
# -----------------------------------------------------------------------------

@patch("requests.post")
def test_openrouter_notice_analysis_flow(mock_post):
    """Verifies that NoticeAnalyzer functions cleanly with OpenRouter client."""
    from notice2action.analysis import NoticeAnalyzer

    mock_llm_json = {
        "issuing_authority": {"value": "Department of Water Resources", "status": "stated", "evidence_quote": "Department of Water Resources"},
        "notice_reference_number": {"value": "WR/2026/044", "status": "stated", "evidence_quote": "Ref: WR/2026/044"},
        "notice_date": {"value": "2026-10-26", "status": "stated", "evidence_quote": "Date: 26-10-2026"},
        "recipient": {"value": "All Irrigation Contractors", "status": "stated", "evidence_quote": "To: All Irrigation Contractors"},
        "main_subject": {"value": "Canal Modernization Tender", "status": "stated", "evidence_quote": "Subject: Canal Modernization Tender"},
        "required_action_and_deadline": {"value": "Submit bids before 15 November 2026", "status": "stated", "evidence_quote": "Submit bids before 15 November 2026"},
        "purpose": {"value": "Procurement of modernization works", "status": "stated", "evidence_quote": "Procurement of modernization works"},
        "eligibility": {"value": "Class A contractors", "status": "stated", "evidence_quote": "Class A contractors"},
        "deadline": {"value": "15 November 2026", "status": "stated", "evidence_quote": "15 November 2026"},
        "fee_or_cost": {"value": "Rs. 5,000", "status": "stated", "evidence_quote": "Rs. 5,000"},
        "required_documents": {"value": "Registration certificate and GST return", "status": "stated", "evidence_quote": "GST return"},
        "contact_details": {"value": "tenders@jal.gov.in", "status": "stated", "evidence_quote": "tenders@jal.gov.in"},
        "required_actions": {"value": "Download tender forms", "status": "stated", "evidence_quote": "Download tender forms"},
        "important_conditions": {"value": "Earnest Money Deposit mandatory", "status": "stated", "evidence_quote": "Earnest Money Deposit mandatory"},
        "missing_information": [],
        "uncertain_or_conflicting_details": []
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": json.dumps(mock_llm_json)}}]
    }
    mock_post.return_value = mock_resp

    client = OpenRouterClient(api_key="mock_key", model="google/gemma-4-26b-a4b-it:free")
    analyzer = NoticeAnalyzer(client=client)

    sample_text = (
        "Department of Water Resources\n"
        "Ref: WR/2026/044 Date: 26-10-2026\n"
        "To: All Irrigation Contractors\n"
        "Subject: Canal Modernization Tender\n"
        "Submit bids before 15 November 2026 with fee Rs. 5,000.\n"
        "Contact: tenders@jal.gov.in"
    )

    result = analyzer.analyze_notice(sample_text)
    assert result.issuing_authority.value == "Department of Water Resources"
    assert result.notice_reference_number.value == "WR/2026/044"
    assert result.deadline.value == "15 November 2026"
    assert result.issuing_authority.status == "stated"
