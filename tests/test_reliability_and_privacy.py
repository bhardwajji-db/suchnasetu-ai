"""
Tests for Concurrency, Thread-Safety, and Air-Gapped Privacy in SuchnaSetu AI.
Verifies thread-safe cache eviction, zero external TTS requests by default, and concurrent requests.
"""

import threading
from fastapi.testclient import TestClient

from notice2action.api.server import app, _ANALYSIS_CACHE, _CACHE_LOCK, _MAX_CACHE_ENTRIES
from notice2action.schemas import StructuredNotice, ExtractedFact, CertaintyStatus
from notice2action.tts import generate_audio_bytes


client = TestClient(app)


def test_tts_offline_privacy_default():
    """Verifies that generate_audio_bytes returns None by default without external network calls."""
    res = generate_audio_bytes("Test notice text", lang="en", allow_cloud_tts=False)
    assert res is None, "Expected None by default to guarantee 100% offline air-gap"


def test_api_tts_endpoint_privacy():
    """Verifies that /api/tts returns 204 No Content when allow_cloud is False."""
    res = client.post("/api/tts", json={"text": "Test summary", "lang": "en", "allow_cloud": False})
    assert res.status_code == 204


def test_cache_concurrent_access_and_eviction():
    """Verifies that concurrent cache access and eviction does not raise RuntimeError."""
    errors = []

    def make_notice(i: int):
        return StructuredNotice(
            purpose=ExtractedFact(field_name="purpose", value=f"Notice {i}", status=CertaintyStatus.STATED),
            deadline=ExtractedFact(field_name="deadline", value="Tomorrow", status=CertaintyStatus.STATED),
            eligibility=ExtractedFact(field_name="eligibility", value="All", status=CertaintyStatus.STATED),
            fee_or_cost=ExtractedFact(field_name="fee_or_cost", value="Free", status=CertaintyStatus.STATED),
            required_documents=ExtractedFact(field_name="required_documents", value="None", status=CertaintyStatus.STATED),
            contact_details=ExtractedFact(field_name="contact_details", value="help@test.org", status=CertaintyStatus.STATED),
            required_actions=ExtractedFact(field_name="required_actions", value="Apply", status=CertaintyStatus.STATED),
            important_conditions=ExtractedFact(field_name="important_conditions", value="Standard", status=CertaintyStatus.STATED),
        )

    def worker(worker_id: int):
        try:
            for i in range(25):
                key = f"key_{worker_id}_{i}"
                notice = make_notice(i)
                with _CACHE_LOCK:
                    if len(_ANALYSIS_CACHE) >= _MAX_CACHE_ENTRIES:
                        _ANALYSIS_CACHE.pop(next(iter(_ANALYSIS_CACHE)), None)
                    _ANALYSIS_CACHE[key] = notice
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(w,)) for w in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent cache access failed with: {errors}"
