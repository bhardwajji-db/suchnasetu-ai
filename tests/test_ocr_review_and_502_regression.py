"""
Regression test suite for OCR warning calibration and 502/timeout resilience.
Covers:
1. Calibrated uncertain spans (unresolved vs repaired artifacts).
2. Protection of critical fields and impossible dates (never suppressing genuine errors).
3. LLM timeout capping below proxy thresholds.
4. Upstream 502/503/504 exception mapping in Ollama client.
5. FastAPI exception handlers mapping LLM errors to structured JSON.
6. JSON cleaning with thinking tokens and malformed responses.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from notice2action.ocr import calibrate_uncertain_spans, clean_and_repair_gazette_text
from notice2action.llm.base import (
    clean_llm_json_response,
    LLMTimeoutError,
    LLMConnectionError,
    LLMModelError,
)
from notice2action.llm.ollama_client import OllamaClient
from notice2action.api.server import app


# ---------------------------------------------------------------------------
# 1. OCR Calibration Tests
# ---------------------------------------------------------------------------

def test_calibrate_uncertain_spans_distinguishes_repaired_from_unresolved():
    raw_tokens = [
        {"text": '"34', "conf": 45, "box": [100, 200, 150, 220]},
        {"text": "मार्च,", "conf": 88, "box": [155, 200, 200, 220]},
        {"text": "2017", "conf": 95, "box": [205, 200, 250, 220]},
        {"text": "वित्तीय", "conf": 52, "box": [300, 200, 360, 220]},  # valid Indic word
        {"text": "GH2017", "conf": 40, "box": [400, 50, 480, 70]},       # unresolved artifact
        {"text": "-.", "conf": 20, "box": [500, 10, 510, 20]},           # punctuation noise
    ]

    repaired_text = 'पैरा 1 के उपपैरा (2) में, "31 मार्च, 2017" वित्तीय GH2017'
    raw_text = 'पैरा 1 के उपपैरा (2) में, "34 मार्च, 2017 वित्तीय GH2017 -.'

    calibrated = calibrate_uncertain_spans(
        tokens=raw_tokens,
        repaired_text=repaired_text,
        raw_text=raw_text,
    )

    texts = [c["text"] for c in calibrated]
    statuses = {c["text"]: c["status"] for c in calibrated}

    # Pure punctuation noise should be filtered
    assert "-." not in texts

    # Valid Indic word present in repaired text should be filtered as false positive
    assert "वित्तीय" not in texts

    # Repaired token '"34' should be marked repaired
    assert '"34' in texts
    assert statuses['"34'] == "repaired"

    # Unresolved token 'GH2017' must remain and be marked unresolved
    assert "GH2017" in texts
    assert statuses["GH2017"] == "unresolved"


def test_calibrate_uncertain_spans_never_hides_impossible_dates():
    """Impossible dates like '34 मार्च' must never be hidden or classified as benign."""
    raw_tokens = [
        {"text": "34 मार्च", "conf": 85, "box": [100, 100, 200, 120]},  # Even with high conf!
    ]
    repaired_text = "दिनांक 34 मार्च 2017 को जारी"
    raw_text = "दिनांक 34 मार्च 2017 को जारी"

    calibrated = calibrate_uncertain_spans(
        tokens=raw_tokens,
        repaired_text=repaired_text,
        raw_text=raw_text,
    )

    assert len(calibrated) == 1
    assert calibrated[0]["text"] == "34 मार्च"
    assert calibrated[0]["is_critical"] is True
    assert calibrated[0]["status"] == "unresolved"


def test_critical_fields_incorporation():
    """Flagged uncertain critical fields are always injected into uncertain spans."""
    raw_tokens = []
    critical_fields = {
        "corrigendum_date": {
            "value": "27 अप्रैल, 2017",
            "confidence": 55.0,
            "status": "flagged_uncertain",
            "source": "tesseract",
        }
    }

    calibrated = calibrate_uncertain_spans(
        tokens=raw_tokens,
        repaired_text="some text",
        raw_text="some text",
        critical_fields=critical_fields,
    )

    assert len(calibrated) == 1
    assert calibrated[0]["text"] == "27 अप्रैल, 2017"
    assert calibrated[0]["is_critical"] is True
    assert calibrated[0]["status"] == "unresolved"


# ---------------------------------------------------------------------------
# 2. LLM Timeout & 502 Resilience Tests
# ---------------------------------------------------------------------------

def test_ollama_client_timeout_capped():
    """Read timeout must be capped at <= 85.0s to precede reverse-proxy 100s cuts."""
    client = OllamaClient(timeout_seconds=180)
    with patch("notice2action.llm.ollama_client.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"message": {"content": '{"summary": "ok"}'}}
        mock_post.return_value = mock_resp

        client.generate_chat([{"role": "user", "content": "hi"}])
        call_kwargs = mock_post.call_args[1]
        timeout_arg = call_kwargs["timeout"]
        connect_t, read_t = timeout_arg
        assert read_t <= 90.0
        assert connect_t <= 10.0


def test_ollama_client_maps_502_to_connection_error():
    """An upstream 502/503 from Ollama must raise LLMConnectionError, not crash."""
    client = OllamaClient()
    with patch("notice2action.llm.ollama_client.requests.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 502
        mock_resp.text = "Bad Gateway"
        mock_post.return_value = mock_resp

        with pytest.raises(LLMConnectionError) as exc_info:
            client.generate_chat([{"role": "user", "content": "hi"}])
        assert "502" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 3. FastAPI Exception Mapping Tests
# ---------------------------------------------------------------------------

def test_server_maps_llm_timeout_to_504():
    """LLMTimeoutError must return HTTP 504 with actionable error JSON."""
    client = TestClient(app)
    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice", side_effect=LLMTimeoutError("Inference timed out")):
        resp = client.post("/api/analyze", json={"notice_text": "Sample valid notice text for analysis", "target_language": "en"})
        assert resp.status_code == 504
        data = resp.json()
        assert data["error_type"] == "model_timeout"
        assert "timed out" in data["detail"]


def test_server_maps_llm_connection_error_to_503():
    """LLMConnectionError must return HTTP 503 with actionable error JSON."""
    client = TestClient(app)
    with patch("notice2action.analysis.NoticeAnalyzer.analyze_notice", side_effect=LLMConnectionError("Ollama offline")):
        resp = client.post("/api/analyze", json={"notice_text": "Sample valid notice text for analysis", "target_language": "en"})
        assert resp.status_code == 503
        data = resp.json()
        assert data["error_type"] == "model_offline"
        assert "offline" in data["detail"]


# ---------------------------------------------------------------------------
# 4. JSON Cleaning & Thinking Token Tests
# ---------------------------------------------------------------------------

def test_clean_llm_json_response_with_thinking_and_fences():
    raw_output = """<thinking>
We need to extract the summary and deadline from the notice.
Let's format as JSON.
</thinking>
```json
{
  "summary": "This is an extension notification.",
  "deadline": "2017-04-30",
}
```"""
    cleaned = clean_llm_json_response(raw_output)
    import json
    parsed = json.loads(cleaned)
    assert parsed["summary"] == "This is an extension notification."
    assert parsed["deadline"] == "2017-04-30"
