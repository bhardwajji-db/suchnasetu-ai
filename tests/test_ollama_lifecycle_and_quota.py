"""
Comprehensive Automated Tests for Ollama Lifecycle, Memory Management,
Guest Quota Counting, Error Separation, and Clean Shutdown.
"""

import time
import os
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

import notice2action.api.server as server_module
from notice2action.api.server import app
from notice2action.config import config
from notice2action.auth.auth_service import auth_service
from notice2action.llm.ollama_client import OllamaClient
from notice2action.llm.base import (
    LLMConnectionError,
    LLMModelError,
    LLMTimeoutError,
    LLMRateLimitError,
    LLMConfigError,
)
from notice2action.schemas import (
    StructuredNotice,
    ExtractedFact,
    CertaintyStatus,
)


@pytest.fixture
def client():
    return TestClient(app)


def _mock_structured_notice() -> StructuredNotice:
    return StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="Solar Subsidy 2026 Application",
            status=CertaintyStatus.STATED,
            evidence_quote="Notice Ref: MNRE-SOLAR-2026-001",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="Residential homeowners in Delhi NCR",
            status=CertaintyStatus.STATED,
            evidence_quote="Eligible: Residential homeowners",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="31 March 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="Last date: 31 March 2026",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="Free registration",
            status=CertaintyStatus.STATED,
            evidence_quote="No application fee",
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="Electricity bill and Aadhaar card",
            status=CertaintyStatus.STATED,
            evidence_quote="Documents required: Electricity bill, Aadhaar card",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="support@mnre.gov.in",
            status=CertaintyStatus.STATED,
            evidence_quote="Email: support@mnre.gov.in",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit online application via portal",
            status=CertaintyStatus.STATED,
            evidence_quote="Action required: Submit online application",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Valid for grid-connected rooftop systems only",
            status=CertaintyStatus.STATED,
            evidence_quote="Condition: Grid-connected rooftop systems only",
        ),
    )


# =============================================================================
# 1. Guest Quota Fixes: Inspection Does NOT Consume, 422 Does NOT Consume
# =============================================================================

def test_guest_status_read_only_does_not_consume_quota(client):
    """Verifies GET /api/auth/guest-status is strictly read-only and never decrements quota."""
    unique_ip = f"198.51.100.{int(time.time() * 1000) % 250 + 1}"
    headers = {"X-Forwarded-For": unique_ip}

    # First check
    res1 = client.get("/api/auth/guest-status", headers=headers)
    assert res1.status_code == 200
    rem1 = res1.json()["remaining_analyses"]

    # Multiple successive status inspections
    for _ in range(5):
        res = client.get("/api/auth/guest-status", headers=headers)
        assert res.status_code == 200
        assert res.json()["remaining_analyses"] == rem1, "Inspecting guest status must not consume quota!"


def test_empty_notice_validation_failure_does_not_consume_quota(client):
    """Verifies that 422 validation failure on empty text does not consume guest quota."""
    unique_ip = f"198.51.101.{int(time.time() * 1000) % 250 + 1}"
    headers = {"X-Forwarded-For": unique_ip}

    # Initial quota check
    res1 = client.get("/api/auth/guest-status", headers=headers)
    init_quota = res1.json()["remaining_analyses"]

    # Attempt to analyze empty string
    res_err = client.post("/api/analyze", json={"notice_text": "   "}, headers=headers)
    assert res_err.status_code == 422
    assert "cannot be empty" in res_err.json()["detail"].lower()

    # Quota must remain identical
    res2 = client.get("/api/auth/guest-status", headers=headers)
    assert res2.json()["remaining_analyses"] == init_quota, "422 validation failure must not consume quota!"


def test_valid_notice_consumes_guest_quota_atomically(client):
    """Verifies valid analysis consumes exactly one quota unit."""
    unique_ip = f"198.51.102.{int(time.time() * 1000) % 250 + 1}"
    headers = {"X-Forwarded-For": unique_ip}

    res1 = client.get("/api/auth/guest-status", headers=headers)
    init_quota = res1.json()["remaining_analyses"]

    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice", return_value=_mock_structured_notice()):
        res = client.post(
            "/api/analyze",
            json={"notice_text": "Government of India MNRE Solar Subsidy Scheme 2026. Last date 31 March 2026."},
            headers=headers,
        )
        assert res.status_code == 200

    res2 = client.get("/api/auth/guest-status", headers=headers)
    after_quota = res2.json()["remaining_analyses"]
    assert after_quota == init_quota - 1, "Exactly one quota unit must be consumed for valid analysis."


def test_guest_quota_exhaustion_returns_429(client):
    """Verifies that exceeding the guest limit returns HTTP 429 without misleading Ollama diagnostics."""
    unique_ip = f"198.51.103.{int(time.time() * 1000) % 250 + 1}"
    headers = {"X-Forwarded-For": unique_ip}

    max_reqs = int(getattr(config, "guest_rate_limit_per_window", 10))

    # Exhaust quota
    for _ in range(max_reqs):
        allowed, remaining = auth_service.consume_guest_quota(unique_ip)
        assert allowed is True

    # Next attempt must be blocked with HTTP 429
    res = client.post(
        "/api/analyze",
        json={"notice_text": "Notice for quota exhaustion test."},
        headers=headers,
    )
    assert res.status_code == 429
    detail = res.json()["detail"]
    assert "quota exceeded" in detail.lower()
    # Ensure it directs citizen to sign in, not blaming Ollama
    assert "sign in" in detail.lower() or "register" in detail.lower()


def test_quota_refund_on_ollama_downtime(client):
    """Verifies that if Ollama is unreachable, the guest is not penalized and quota is refunded."""
    unique_ip = f"198.51.104.{int(time.time() * 1000) % 250 + 1}"
    headers = {"X-Forwarded-For": unique_ip}

    res1 = client.get("/api/auth/guest-status", headers=headers)
    init_quota = res1.json()["remaining_analyses"]

    with patch(
        "notice2action.analysis.NoticeAnalyzer.analyze_notice",
        side_effect=LLMConnectionError("Cannot connect to Ollama at http://127.0.0.1:11434. Connection refused."),
    ):
        res = client.post(
            "/api/analyze",
            json={"notice_text": "Testing connection failure refund handling."},
            headers=headers,
        )
        assert res.status_code == 503
        data = res.json()
        assert data["error_type"] in ("model_offline", "LLMConnectionError")

    # Verify quota was refunded
    res2 = client.get("/api/auth/guest-status", headers=headers)
    assert res2.json()["remaining_analyses"] == init_quota, "Quota must be refunded on LLM connection failure!"


# =============================================================================
# 2. Ollama Memory Management: Keep-Alive, Unload & Warmup
# =============================================================================

def test_ollama_client_keep_alive_configuration():
    """Verifies OllamaClient respects keep_alive config and defaults to 5m."""
    client = OllamaClient()
    assert client.keep_alive in ("5m", config.ollama_keep_alive)

    custom_client = OllamaClient(keep_alive="10m")
    assert custom_client.keep_alive == "10m"


def test_ollama_client_generate_chat_sends_keep_alive():
    """Verifies generate_chat includes keep_alive in Ollama payload."""
    client = OllamaClient(keep_alive="5m")

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": {"content": '{"purpose": "Test"}'}}
        mock_post.return_value = mock_resp

        client.generate_chat([{"role": "user", "content": "Analyze notice"}])
        assert mock_post.called
        sent_payload = mock_post.call_args[1]["json"]
        assert sent_payload["keep_alive"] == "5m"


def test_ollama_client_unload_model_sends_zero_keep_alive():
    """Verifies unload_model sends keep_alive: 0 to unload VRAM."""
    client = OllamaClient()

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = client.unload_model()
        assert result is True
        sent_payload = mock_post.call_args[1]["json"]
        assert sent_payload["keep_alive"] == 0
        assert sent_payload["model"] == client.model


def test_ollama_client_warmup():
    """Verifies warmup probe sends lightweight 1-token prediction."""
    client = OllamaClient()

    with patch("requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        warmup_res = client.warmup()
        assert warmup_res["status"] == "ready"
        sent_payload = mock_post.call_args[1]["json"]
        assert sent_payload["options"]["num_predict"] == 1


# =============================================================================
# 3. Active Request Tracking & Ollama Unload Endpoint
# =============================================================================

def test_active_requests_status_endpoint(client):
    """Verifies GET /api/status/active-requests reports current concurrency."""
    res = client.get("/api/status/active-requests")
    assert res.status_code == 200
    assert "active_requests" in res.json()
    assert res.json()["active_requests"] == 0


def test_ollama_unload_endpoint_safety(client):
    """Verifies POST /api/ollama/unload blocks unloading when active requests > 0."""
    # Idle unload should succeed
    with patch("notice2action.llm.ollama_client.OllamaClient.unload_model", return_value=True):
        res = client.post("/api/ollama/unload")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    # Simulate active in-flight request on module global
    with server_module._ACTIVE_COUNTER_LOCK:
        server_module._ACTIVE_ANALYSIS_COUNTER = 1

    try:
        res_busy = client.post("/api/ollama/unload")
        assert res_busy.status_code == 409
        assert "in progress" in res_busy.json()["detail"].lower()
    finally:
        with server_module._ACTIVE_COUNTER_LOCK:
            server_module._ACTIVE_ANALYSIS_COUNTER = 0


# =============================================================================
# 4. Error Categorization: Distinguishing 503 Offline vs 503 Missing vs 504 Timeout
# =============================================================================

def test_exception_handler_model_missing_503(client):
    """Verifies missing model error is returned as 503 LLMModelError."""
    with patch(
        "notice2action.analysis.NoticeAnalyzer.analyze_notice",
        side_effect=LLMModelError("Model 'gemma4:latest' not found in Ollama repository."),
    ):
        res = client.post("/api/analyze", json={"notice_text": "Sample text for model missing."})
        assert res.status_code == 503
        data = res.json()
        assert data["error_type"] in ("model_missing", "LLMModelError")
        assert "gemma4:latest" in data["detail"]


def test_exception_handler_inference_timeout_504(client):
    """Verifies inference timeout error is returned as 504 LLMTimeoutError."""
    with patch(
        "notice2action.analysis.NoticeAnalyzer.analyze_notice",
        side_effect=LLMTimeoutError("Gemma 4 inference timed out after 120 seconds."),
    ):
        res = client.post("/api/analyze", json={"notice_text": "Sample text for timeout test."})
        assert res.status_code == 504
        data = res.json()
        assert data["error_type"] in ("model_timeout", "LLMTimeoutError")
        assert "timed out" in data["detail"]


# =============================================================================
# 5. Launcher Script Presence & Ownership Logic Verification
# =============================================================================

def test_windows_launcher_script_presence_and_ownership_logic():
    """Verifies run_sochnasetu.ps1 exists, contains lifecycle checks, and does NOT kill pre-existing Ollama."""
    project_root = Path(__file__).resolve().parent.parent
    launcher_path = project_root / "run_sochnasetu.ps1"

    assert launcher_path.exists(), "run_sochnasetu.ps1 must exist at project root."

    content = launcher_path.read_text(encoding="utf-8")

    # Verify lifecycle states
    assert "Starting Ollama" in content
    assert "Checking model" in content
    assert "Loading model" in content
    assert "gemma4:latest" in content

    # Verify external Ollama preservation logic
    assert "OllamaPreExisting" in content
    assert "PRESERVED" in content
    assert "Stop-SochnaSetuServices" in content

    # Verify unconsented download protection
    assert "without unconsented" in content or "unconsented automatic" in content
