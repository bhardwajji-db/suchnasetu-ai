"""
Tests for Demo Library API and Language Detection Endpoints.
"""

from fastapi.testclient import TestClient
from notice2action.api.server import app

client = TestClient(app)


def test_get_demo_library():
    """Tests GET /api/demo-library returns registered demo notices."""
    response = client.get("/api/demo-library")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 30
    assert any(d["id"] == "DEMO-01" for d in data)


def test_filter_demo_library_by_language():
    """Tests filtering demos by language."""
    response = client.get("/api/demo-library?source_lang=hi")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    for item in data:
        assert item["source_lang"] == "hi"


def test_filter_demo_library_by_format():
    """Tests filtering demos by file format."""
    response = client.get("/api/demo-library?format_type=docx")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    for item in data:
        assert item["format"] == "docx"


def test_load_demo_library_item():
    """Tests loading a demo file and running the ingestion pipeline."""
    response = client.post("/api/demo-library/DEMO-01/load")
    assert response.status_code == 200
    data = response.json()
    assert data["demo_id"] == "DEMO-01"
    assert "NATIONAL MERIT SCHOLARSHIP" in data["raw_text"].upper()
    assert data["char_count"] > 100
    assert data["fingerprint"] != ""
    assert data["ground_truth"]["authority"] is not None


def test_load_nonexistent_demo():
    """Tests loading a demo with an invalid ID returns 404."""
    response = client.post("/api/demo-library/DEMO-NONEXISTENT/load")
    assert response.status_code == 404


def test_detect_language_endpoint():
    """Tests language detection endpoint across scripts."""
    # Hindi text
    hi_resp = client.post("/api/language/detect", json={"text": "राष्ट्रीय प्रौद्योगिकी संस्थान नई दिल्ली प्रवेश प्रक्रिया"})
    assert hi_resp.status_code == 200
    assert hi_resp.json()["detected_language"] == "hi"

    # Bengali text
    bn_resp = client.post("/api/language/detect", json={"text": "পশ্চিমবঙ্গ কেন্দ্রীয় বিশ্ববিদ্যালয় পরীক্ষা নির্দেশিকা"})
    assert bn_resp.status_code == 200
    assert bn_resp.json()["detected_language"] == "bn"

    # Tamil text
    ta_resp = client.post("/api/language/detect", json={"text": "தமிழ்நாடு குடிநீர் வழங்கல் மற்றும் வடிகால் வாரியம்"})
    assert ta_resp.status_code == 200
    assert ta_resp.json()["detected_language"] == "ta"

    # Urdu text
    ur_resp = client.post("/api/language/detect", json={"text": "قومی کونسل برائے فروغ اردو زبان نئی دہلی تعلیمی وظائف"})
    assert ur_resp.status_code == 200
    assert ur_resp.json()["detected_language"] == "ur"
