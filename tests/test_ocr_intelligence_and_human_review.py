import os
import tempfile
from pathlib import Path
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from notice2action.language_detection import (
    detect_image_language,
    get_ocr_language_for_detection,
    detect_document_language,
)
from notice2action.ocr import (
    detect_image_orientation,
    extract_text_from_image,
)
from notice2action.storage.db import DatabaseManager
from notice2action.api.server import app

client = TestClient(app)

IIMT_IMAGE_PATH = "data/uploads/f1cfda07c4ed0c86_1794773110.jpeg"
GAZETTE_IMAGE_PATH = "data/samples/gazette_corrigendum_2017.jpeg"


class TestLanguageDetectionAndOrientation:
    def test_iimt_notice_auto_language_detection(self):
        """Verify IIMT notice is detected as English and selects 'eng' mode."""
        assert os.path.exists(IIMT_IMAGE_PATH), f"Missing test image: {IIMT_IMAGE_PATH}"
        img = Image.open(IIMT_IMAGE_PATH).convert("RGB")

        detection = detect_image_language(img)
        assert detection.detected_language in ("en", "eng")
        assert detection.confidence >= 0.8
        assert detection.is_mixed is False

        ocr_lang = get_ocr_language_for_detection(detection)
        assert ocr_lang == "eng"

    def test_gazette_notice_auto_language_detection(self):
        """Verify Hindi Gazette notice is detected as Hindi/Bilingual."""
        if not os.path.exists(GAZETTE_IMAGE_PATH):
            pytest.skip(f"Missing sample: {GAZETTE_IMAGE_PATH}")
        img = Image.open(GAZETTE_IMAGE_PATH).convert("RGB")

        detection = detect_image_language(img)
        assert detection.detected_language in ("hi", "hin")
        assert detection.confidence >= 0.6

        ocr_lang = get_ocr_language_for_detection(detection)
        assert "hin" in ocr_lang

    def test_iimt_orientation_stays_upright_zero_degrees(self):
        """Verify IIMT notice is not falsely rotated 90 or 270 degrees."""
        img = Image.open(IIMT_IMAGE_PATH).convert("RGB")
        img_out, angle = detect_image_orientation(img)
        assert angle == 0, f"Expected 0 degrees upright, got {angle}"

    def test_ocr_extract_text_auto_language(self):
        """Verify extract_text_from_image with target_lang='auto' detects English and extracts key notice terms."""
        img = Image.open(IIMT_IMAGE_PATH).convert("RGB")
        res = extract_text_from_image(img, target_lang="auto")

        assert res.detected_language in ("en", "eng")
        assert res.language_confidence >= 0.8
        assert res.orientation_applied == 0

        # Critical notice content should be recovered cleanly
        text = res.extracted_text
        assert "IIMT" in text or "ENGINEERING" in text
        assert "2026" in text or "Notice" in text or "Auditorium" in text


class TestHumanReviewPersistenceAndDB:
    def setup_method(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        self.db = DatabaseManager(db_path=self.db_path)
        self.doc = self.db.save_document(
            raw_text="IIMT Notice Raw Text with error: Ref No IIMT/IQAC/2026-27/11 date 29.10.2026",
            filename="notice.txt",
        )

    def teardown_method(self):
        self.db.close()
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_save_and_retrieve_review_items(self):
        items = [
            {
                "id": "rev_1",
                "document_id": self.doc.id,
                "page_number": 1,
                "box": [10, 20, 100, 40],
                "original_text": "IIMT/IQAC",
                "corrected_text": None,
                "confidence": 65.0,
                "reason": "low confidence token",
                "status": "pending",
            },
            {
                "id": "rev_2",
                "document_id": self.doc.id,
                "page_number": 1,
                "box": [50, 60, 120, 80],
                "original_text": "29.10.2026",
                "corrected_text": None,
                "confidence": 55.0,
                "reason": "date format check",
                "status": "pending",
            },
        ]
        saved_items = self.db.save_human_review_items(self.doc.id, items)
        assert len(saved_items) == 2

        summary = self.db.get_human_review_items(self.doc.id)
        assert summary["total"] == 2
        assert summary["pending"] == 2
        assert summary["corrected"] == 0
        assert summary["verified"] == 0
        assert summary["ignored"] == 0

    def test_update_review_item_status_and_correction(self):
        items = [
            {
                "id": "rev_item_a",
                "document_id": self.doc.id,
                "page_number": 1,
                "box": [10, 20, 100, 40],
                "original_text": "error",
                "corrected_text": None,
                "confidence": 50.0,
                "status": "pending",
            }
        ]
        self.db.save_human_review_items(self.doc.id, items)

        # Update to corrected
        updated = self.db.update_human_review_item("rev_item_a", "corrected", "corrected_word")
        assert updated is not None
        assert updated["corrected"] == 1
        assert updated["pending"] == 0

        summary = self.db.get_human_review_items(self.doc.id)
        assert summary["corrected"] == 1
        assert summary["pending"] == 0
        assert summary["items"][0]["corrected_text"] == "corrected_word"
        assert summary["items"][0]["status"] == "corrected"

    def test_apply_review_corrections_updates_document_text(self):
        items = [
            {
                "id": "rev_item_1",
                "document_id": self.doc.id,
                "page_number": 1,
                "box": [10, 20, 100, 40],
                "original_text": "error",
                "suggested_text": "success",
                "confidence": 45.0,
                "status": "pending",
            },
            {
                "id": "rev_item_2",
                "document_id": self.doc.id,
                "page_number": 1,
                "box": [10, 50, 100, 70],
                "original_text": "Ref. No. :",
                "suggested_text": "Ref. No. :",
                "confidence": 95.0,
                "status": "pending",
            }
        ]
        self.db.save_human_review_items(self.doc.id, items)

        # Mark item 1 as corrected with explicit text
        self.db.update_human_review_item("rev_item_1", "corrected", "success_fixed")
        # Mark item 2 as verified (keeps existing corrected/suggested text)
        self.db.update_human_review_item("rev_item_2", "verified")

        res = self.db.apply_review_corrections(self.doc.id)
        assert res["applied_count"] >= 1
        assert "success_fixed" in res["raw_text"]
        assert "error" not in res["raw_text"]

        # Check DB reflects updated canonical text while preserving raw
        doc = self.db.get_document(self.doc.id)
        assert doc is not None
        assert "success" in doc.raw_text


class TestServerEndpoints:
    def test_detect_language_endpoint(self):
        with open(IIMT_IMAGE_PATH, "rb") as f:
            file_bytes = f.read()

        response = client.post(
            "/api/ocr/detect-language",
            files={"file": ("10.jpeg", file_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_language"] in ("en", "eng")
        assert data["suggested_ocr_lang"] == "eng"
        assert data["confidence"] >= 0.8

    def test_ocr_endpoint_with_auto_language_and_persistence(self):
        with open(IIMT_IMAGE_PATH, "rb") as f:
            file_bytes = f.read()

        response = client.post(
            "/api/ocr",
            data={"target_lang": "auto", "enhance_contrast": "false"},
            files={"file": ("10.jpeg", file_bytes, "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["detected_language"] in ("en", "eng")
        assert data["document_id"] is not None
        doc_id = data["document_id"]

        # Test querying review items for this newly created document
        rev_resp = client.get(f"/api/documents/{doc_id}/review-items")
        assert rev_resp.status_code == 200
        rev_data = rev_resp.json()
        assert "total" in rev_data
        assert "items" in rev_data
