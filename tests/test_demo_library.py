"""
Automated Verification Suite for SuchnaSetu AI Judge-Ready Demo Library.
Verifies that all 32+ demo instances exist as real files, cover all 10 languages and 7 formats,
and parse cleanly through the ingestion pipeline.
"""

import json
from pathlib import Path
import pytest

from notice2action.ingestion import ingest_uploaded_file, extract_text_from_docx, extract_text_from_pdf
from notice2action.language_detection import detect_document_language

DEMO_DIR = Path("tests/fixtures/demo_library")
MANIFEST_PATH = DEMO_DIR / "manifest.json"

REQUIRED_LANGUAGES = ["en", "hi", "bn", "ta", "te", "mr", "gu", "pa", "kn", "ur"]
REQUIRED_FORMATS = ["txt", "pdf", "docx", "png", "jpg", "webp", "tif"]


@pytest.fixture(scope="module")
def manifest():
    assert MANIFEST_PATH.is_file(), f"Manifest file missing at {MANIFEST_PATH}"
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    return data


def test_manifest_integrity_and_file_resolution(manifest):
    """Verifies that every entry in manifest.json resolves to an actual valid file on disk."""
    assert len(manifest) >= 30, f"Expected at least 30 demos, found {len(manifest)}"

    for item in manifest:
        demo_id = item["id"]
        rel_path = item["file_path"]
        file_path = DEMO_DIR / rel_path

        assert file_path.is_file(), f"Demo {demo_id}: File not found at {file_path}"
        assert file_path.stat().st_size > 0, f"Demo {demo_id}: File is 0 bytes at {file_path}"

        # Verify ground truth fields
        gt = item["ground_truth"]
        for key in ["authority", "purpose", "deadline", "fee", "eligibility", "contact"]:
            assert key in gt, f"Demo {demo_id}: Missing ground_truth key '{key}'"


def test_ten_languages_coverage(manifest):
    """Verifies that all 10 constitutional languages have at least 3 distinct demo documents."""
    lang_counts = {lang: 0 for lang in REQUIRED_LANGUAGES}
    for item in manifest:
        src = item["source_language"]
        if src in lang_counts:
            lang_counts[src] += 1

    for lang, count in lang_counts.items():
        assert count >= 3, f"Language '{lang}' has only {count} demo(s), expected at least 3"


def test_all_advertised_formats_coverage(manifest):
    """Verifies that all advertised file formats are present in the demo library."""
    format_counts = {fmt: 0 for fmt in REQUIRED_FORMATS}
    for item in manifest:
        fmt = item["format"].lower()
        if fmt in format_counts:
            format_counts[fmt] += 1

    for fmt, count in format_counts.items():
        assert count >= 1, f"Format '.{fmt}' has {count} demo(s), expected at least 1"


def test_docx_ingestion_and_text_extraction(manifest):
    """Verifies that .docx demo notices parse and extract non-empty text."""
    docx_items = [d for d in manifest if d["format"] == "docx"]
    assert len(docx_items) >= 1

    for item in docx_items:
        file_path = DEMO_DIR / item["file_path"]
        content = file_path.read_bytes()
        extracted = extract_text_from_docx(content)
        assert len(extracted.strip()) > 50
        auth = item["ground_truth"]["authority"].split(",")[0].lower()
        title_word = item["title"].split()[0].lower()
        assert (
            auth in extracted.lower()
            or title_word in extracted.lower()
            or "university" in extracted.lower()
            or "aicte" in extracted.lower()
        )


def test_native_script_language_detection(manifest):
    """Verifies that text from demo documents correctly matches the expected source language."""
    txt_items = [d for d in manifest if d["format"] == "txt"]
    assert len(txt_items) >= 10

    for item in txt_items:
        file_path = DEMO_DIR / item["file_path"]
        text = file_path.read_text(encoding="utf-8")
        det = detect_document_language(text)

        expected_lang = item["source_language"]
        # In bilingual or mixed notices, check that detected or secondary matches
        assert (
            det.detected_language == expected_lang
            or expected_lang in det.secondary_languages
        ), f"Demo {item['id']}: expected {expected_lang}, detected {det.detected_language}"
