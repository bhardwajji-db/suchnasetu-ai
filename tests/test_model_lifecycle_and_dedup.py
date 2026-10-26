"""
Tests for Ollama Model Lifecycle, Error Classification/Separation, and In-Flight Request Deduplication.
Verifies HackDay Readiness requirements:
- Model status, warmup, and unload endpoints
- Accurate separation of Guest Quota (429), Model Timeout (504), Model Offline (503), OCR (422)
- In-flight duplicate inference prevention
"""

import asyncio
import time
import concurrent.futures
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from notice2action.api.server import app, _ANALYSIS_CACHE, _CACHE_LOCK
from notice2action.llm.base import (
    LLMTimeoutError,
    LLMConnectionError,
    LLMRateLimitError,
    LLMConfigError,
)
from notice2action.schemas import StructuredNotice, ExtractedFact, CertaintyStatus
from notice2action.storage.db import get_db


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_test_state():
    """Isolate tests from shared rate limits."""
    db = get_db()
    conn = db.get_connection()
    with conn:
        conn.execute("DELETE FROM rate_limits;")


def test_model_status_endpoint():
    """GET /api/models/status returns Ollama provider status and model info."""
    resp = client.get("/api/models/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "ollama"
    assert "target_model" in data
    assert "loaded_models_count" in data
    assert isinstance(data["loaded_models"], list)


def test_model_warmup_and_unload_endpoints():
    """POST /api/models/warmup and /api/models/unload return structured status."""
    with patch("notice2action.llm.ollama_client.OllamaClient.warmup") as mock_warmup:
        mock_warmup.return_value = {"success": True, "model": "gemma4:latest", "message": "Pre-warmed"}
        resp = client.post("/api/models/warmup")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    with patch("notice2action.llm.ollama_client.OllamaClient.unload_model") as mock_unload:
        mock_unload.return_value = {"success": True, "model": "gemma4:latest", "message": "Unloaded"}
        resp = client.post("/api/models/unload")
        assert resp.status_code == 200
        assert resp.json()["success"] is True


def test_error_separation_model_timeout():
    """LLMTimeoutError maps accurately to HTTP 504 with error_type='model_timeout'."""
    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice") as mock_analyze:
        mock_analyze.side_effect = LLMTimeoutError("Gemma 4 inference timed out after 90 seconds.")
        resp = client.post(
            "/api/analyze",
            json={"notice_text": "Sample timeout test notice content for error verification."},
            headers={"X-Forwarded-For": "192.168.1.101"}
        )
        assert resp.status_code == 504
        data = resp.json()
        assert data["error_type"] == "model_timeout"
        assert data["category"] == "model"
        assert "timed out" in data["detail"].lower()


def test_error_separation_model_offline():
    """LLMConnectionError maps accurately to HTTP 503 with error_type='model_offline'."""
    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice") as mock_analyze:
        mock_analyze.side_effect = LLMConnectionError("Cannot connect to Ollama at http://127.0.0.1:11434.")
        resp = client.post(
            "/api/analyze",
            json={"notice_text": "Sample offline test notice content for error verification."},
            headers={"X-Forwarded-For": "192.168.1.102"}
        )
        assert resp.status_code == 503
        data = resp.json()
        assert data["error_type"] == "model_offline"
        assert data["category"] == "model"
        assert "cannot connect" in data["detail"].lower()


def test_error_separation_guest_quota():
    """Exceeding guest quota maps accurately to HTTP 429 with guest quota message."""
    with patch("notice2action.auth.auth_service.auth_service.check_guest_rate_limit") as mock_rate:
        mock_rate.return_value = (False, 0)
        resp = client.post(
            "/api/analyze",
            json={"notice_text": "Sample quota test notice content."},
            headers={"X-Forwarded-For": "192.168.1.103"}
        )
        assert resp.status_code == 429
        assert "quota exceeded" in resp.json()["detail"].lower()


def test_error_separation_ocr_invalid_image():
    """Posting corrupted or non-image bytes to /api/ocr returns HTTP 400 with invalid image detail."""
    resp = client.post(
        "/api/ocr",
        files={"file": ("corrupt.png", b"NOT_A_VALID_IMAGE_DATA_BYTES", "image/png")}
    )
    assert resp.status_code == 400
    assert "invalid image" in resp.json()["detail"].lower()


def test_in_flight_deduplication_prevents_duplicate_inference():
    """Concurrent requests for identical un-cached notice text share one single inference."""
    call_count = 0

    def mock_slow_analyze(text):
        nonlocal call_count
        call_count += 1
        time.sleep(0.3)  # Simulate slow local LLM inference
        return StructuredNotice(
            purpose=ExtractedFact(field_name="purpose", value="Deduplication Test Notice", status=CertaintyStatus.STATED),
            deadline=ExtractedFact(field_name="deadline", value="30 November 2026", status=CertaintyStatus.STATED),
            eligibility=ExtractedFact(field_name="eligibility", value="All students", status=CertaintyStatus.STATED),
            fee_or_cost=ExtractedFact(field_name="fee_or_cost", value="Free", status=CertaintyStatus.STATED),
            required_documents=ExtractedFact(field_name="required_documents", value="None", status=CertaintyStatus.STATED),
            contact_details=ExtractedFact(field_name="contact_details", value="contact@dedup.test", status=CertaintyStatus.STATED),
            required_actions=ExtractedFact(field_name="required_actions", value="Check in", status=CertaintyStatus.STATED),
            important_conditions=ExtractedFact(field_name="important_conditions", value="None", status=CertaintyStatus.STATED),
            raw_notice_text=text,
        )

    unique_notice = f"Unique deduplication notice content timestamp {time.time_ns()}."

    # Clear cache to ensure fresh start
    with _CACHE_LOCK:
        _ANALYSIS_CACHE.clear()

    async def _run_concurrent():
        from httpx import AsyncClient, ASGITransport
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
            headers = {"X-Forwarded-For": "192.168.1.104"}
            return await asyncio.gather(
                ac.post("/api/analyze", json={"notice_text": unique_notice}, headers=headers),
                ac.post("/api/analyze", json={"notice_text": unique_notice}, headers=headers),
                ac.post("/api/analyze", json={"notice_text": unique_notice}, headers=headers),
            )

    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice", side_effect=mock_slow_analyze), \
         patch("notice2action.auth.auth_service.auth_service.consume_guest_quota", return_value=(True, 10)), \
         patch("notice2action.auth.auth_service.auth_service.check_guest_rate_limit", return_value=(True, 10)):
        r1, r2, r3 = asyncio.run(_run_concurrent())

    # All 3 requests must succeed
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 200

    # But underlying heavy LLM inference must be called ONLY ONCE!
    assert call_count == 1, f"Expected 1 inference call due to deduplication, but got {call_count}"
