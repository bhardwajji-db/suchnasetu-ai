"""
Test Suite for Hindi OCR and Language Pack Diagnostics in SuchnaSetu AI (PS02).
Verifies:
- Auto-detection of Hindi trained data (hin.traineddata) in assets/tessdata
- Clear diagnostics when Hindi language pack is absent
- Safe failure mode: never silently returning English OCR gibberish as Hindi
- Bilingual (eng+hin) and pure Hindi OCR execution
- Preflight diagnostics reporting of Hindi OCR readiness
"""

from pathlib import Path
from unittest.mock import patch
import pytest
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.config import config, run_preflight_diagnostics
from notice2action.ocr import (
    get_available_tesseract_languages,
    extract_text_from_image,
    OCRResult,
    TesseractOCREngine,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_hindi_traineddata_detected_in_assets():
    """Verifies that hin.traineddata is present and detected by Tesseract."""
    langs = get_available_tesseract_languages()
    assert "hin" in langs, (
        f"Expected 'hin' in available Tesseract languages, got {langs}. "
        f"Ensure 'hin.traineddata' exists at assets/tessdata/."
    )
    assert "eng" in langs


def test_preflight_reports_hindi_language_support():
    """Verifies preflight diagnostics reports Hindi OCR capability clearly."""
    report = run_preflight_diagnostics()
    tesseract_item = next((i for i in report.items if i.name == "Tesseract OCR"), None)
    assert tesseract_item is not None
    assert tesseract_item.status == "ok"
    assert "hin" in tesseract_item.details


def test_never_silently_fallback_when_pure_hindi_missing():
    """
    CRITICAL SAFETY REQUIREMENT:
    When pure Hindi OCR is requested ('hin') and hin.traineddata is missing,
    the pipeline MUST return an explicit diagnostic error and NEVER silently
    run English OCR to produce Latin gibberish.
    """
    engine = TesseractOCREngine()
    dummy_img = Image.new("RGB", (300, 100), color=(255, 255, 255))

    with patch("notice2action.ocr.get_available_tesseract_languages", return_value=["eng", "osd"]):
        res = engine.extract_text(dummy_img, target_lang="hin")
        assert res.extracted_text == "", "Extracted text must be empty when requested language is unavailable"
        assert res.is_uncertain is True
        assert res.error is not None
        assert "hin.traineddata" in res.error
        assert "English OCR cannot transcribe Devanagari" in res.error


def test_bilingual_fallback_warning_when_hindi_missing():
    """
    When bilingual OCR ('eng+hin') is requested but Hindi is missing,
    the pipeline should fall back to English with an explicit warning and uncertainty flag.
    """
    engine = TesseractOCREngine()
    dummy_img = Image.new("RGB", (300, 100), color=(255, 255, 255))
    d = ImageDraw.Draw(dummy_img)
    d.text((10, 30), "NOTICE 2026", fill=(0, 0, 0))

    with patch("notice2action.ocr.get_available_tesseract_languages", return_value=["eng", "osd"]):
        res = engine.extract_text(dummy_img, target_lang="eng+hin")
        assert res.warning is not None
        assert "hin.traineddata" in res.warning
        assert "Only English text could be recognized" in res.warning


def test_hindi_ocr_execution_when_traineddata_present():
    """
    Verifies that Hindi OCR executes without crashing when hin.traineddata is available.
    """
    fixture_path = Path("tests/fixtures/synthetic_notice_ocr.png")
    if not fixture_path.is_file():
        pytest.skip("synthetic_notice_ocr.png not found")

    img = Image.open(fixture_path)
    engine = TesseractOCREngine()
    res = engine.extract_text(img, target_lang="eng+hin")
    assert res.error is None
    assert res.extracted_text != ""
    assert res.languages_used == "eng+hin"
    assert res.confidence_score > 0.0


def test_api_ocr_endpoint_supports_hindi_parameter(client):
    """Verifies that the /api/ocr endpoint accepts target_lang='hin' and returns structured metadata."""
    fixture_path = Path("tests/fixtures/synthetic_notice_ocr.png")
    if not fixture_path.is_file():
        pytest.skip("synthetic_notice_ocr.png not found")

    with open(fixture_path, "rb") as f:
        files = {"file": ("notice.png", f.read(), "image/png")}

    data = {"target_lang": "eng+hin", "enhance_contrast": "true"}
    resp = client.post("/api/ocr", files=files, data=data)
    assert resp.status_code == 200
    res_data = resp.json()
    assert "extracted_text" in res_data
    assert res_data["languages_used"] in ["eng+hin", "hin"]
    assert "fingerprint" in res_data
