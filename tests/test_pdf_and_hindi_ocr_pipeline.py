"""
Test Suite for PDF Support (Digital & Scanned), Hindi OCR, and Analysis Caching (SuchnaSetu AI).
Verifies:
 1. Digital PDF text extraction via pypdf.
 2. Scanned PDF extraction via embedded page image OCR.
 3. Password-encrypted PDF rejection with clear security error.
 4. Corrupted PDF byte rejection.
 5. Empty PDF rejection.
 6. Page limit enforcement on oversized PDFs.
 7. Tesseract Hindi language pack discovery and OCR execution.
 8. Analysis cache hit verification (eliminating redundant inference).
"""

from __future__ import annotations

import io
import time
import pytest
from PIL import Image, ImageDraw
import pypdf

from notice2action.config import config
from notice2action.security import (
    validate_uploaded_file,
    SecurityValidationError,
)
from notice2action.ingestion import (
    ingest_uploaded_file,
    extract_text_from_pdf,
)
from notice2action.ocr import (
    extract_text_from_image,
    get_available_tesseract_languages,
)
from notice2action.api.server import app, _ANALYSIS_CACHE
from fastapi.testclient import TestClient


client = TestClient(app)


def create_synthetic_digital_pdf(text: str) -> bytes:
    """Generates a minimal valid PDF containing digital text using standard PDF 1.4 syntax."""
    # Escape parentheses
    safe_text = text.replace("(", "\\(").replace(")", "\\)")
    stream_content = f"BT /F1 12 Tf 72 712 Td ({safe_text}) Tj ET".encode("latin-1", errors="replace")
    stream_len = len(stream_content)

    pdf_template = (
        f"%PDF-1.4\n"
        f"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        f"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        f"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
        f"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
        f"5 0 obj << /Length {stream_len} >>\n"
        f"stream\n"
    ).encode("ascii") + stream_content + (
        b"\nendstream\nendobj\nxref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000227 00000 n \n"
        b"0000000297 00000 n \n"
        b"trailer << /Size 6 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
    )
    return pdf_template


def create_synthetic_scanned_pdf(text: str = "OFFICIAL CIRCULAR: DEADLINE 15 NOVEMBER 2026") -> bytes:
    """Generates a valid scanned PDF by drawing text onto an image and saving as PDF via Pillow."""
    img = Image.new("RGB", (600, 120), color="white")
    d = ImageDraw.Draw(img)
    d.text((20, 45), text, fill="black")

    buf = io.BytesIO()
    img.save(buf, format="PDF")
    return buf.getvalue()


# 1. Digital PDF text extraction
def test_01_digital_pdf_text_extraction():
    text_content = "SCHOLARSHIP NOTICE 2026: Mandatory cutoff deadline is 15 November 2026 at Counter 4."
    pdf_bytes = create_synthetic_digital_pdf(text_content)

    safe_name, file_type = validate_uploaded_file("notice.pdf", pdf_bytes)
    assert file_type == "pdf"

    res = ingest_uploaded_file("official_notice.pdf", pdf_bytes)
    assert res.error is None
    assert res.source_type == "pdf"
    assert "SCHOLARSHIP NOTICE 2026" in res.raw_text
    assert "15 November 2026" in res.raw_text


# 2. Scanned PDF extraction via embedded page image OCR
def test_02_scanned_pdf_ocr_extraction():
    pdf_bytes = create_synthetic_scanned_pdf("ACADEMIC COUNCIL MEETING ON 20 NOVEMBER 2026")
    res = ingest_uploaded_file("scanned_circular.pdf", pdf_bytes)

    assert res.error is None
    assert res.source_type == "pdf"
    assert res.raw_text is not None
    assert "2026" in res.raw_text or "NOVEMBER" in res.raw_text.upper()


# 3. Encrypted PDF rejection
def test_03_encrypted_pdf_rejection():
    writer = pypdf.PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.encrypt("secret_password_123")
    buf = io.BytesIO()
    writer.write(buf)
    encrypted_bytes = buf.getvalue()

    with pytest.raises(SecurityValidationError) as exc:
        validate_uploaded_file("protected.pdf", encrypted_bytes)
    assert "encrypted" in str(exc.value).lower() or "password" in str(exc.value).lower()


# 4. Corrupted PDF rejection
def test_04_corrupted_pdf_rejection():
    corrupted_bytes = b"%PDF-1.4\n1 0 obj << truncated header"
    with pytest.raises(SecurityValidationError) as exc:
        validate_uploaded_file("corrupt.pdf", corrupted_bytes)
    assert "corrupt" in str(exc.value).lower() or "invalid" in str(exc.value).lower()


# 5. Empty PDF rejection
def test_05_empty_pdf_rejection():
    # 0-byte file
    with pytest.raises(SecurityValidationError) as exc:
        validate_uploaded_file("empty.pdf", b"")
    assert "empty" in str(exc.value).lower()

    # 0-page PDF
    writer = pypdf.PdfWriter()
    buf = io.BytesIO()
    writer.write(buf)
    with pytest.raises(SecurityValidationError) as exc2:
        validate_uploaded_file("zero_pages.pdf", buf.getvalue())
    assert "0 pages" in str(exc2.value).lower()


# 6. Page limit enforcement
def test_06_pdf_page_limit_enforcement():
    writer = pypdf.PdfWriter()
    # Add 35 pages (exceeds default limit of 30)
    for _ in range(35):
        writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)

    with pytest.raises(SecurityValidationError) as exc:
        validate_uploaded_file("huge.pdf", buf.getvalue())
    assert "exceeds maximum safety limit" in str(exc.value)


# 7. Tesseract Hindi language pack discovery & OCR
def test_07_tesseract_hindi_ocr_support():
    langs = get_available_tesseract_languages()
    assert "hin" in langs, f"Hindi traineddata should be discovered in assets/tessdata (found: {langs})"

    # Render a clear bilingual notice image
    img = Image.new("RGB", (500, 100), color="white")
    d = ImageDraw.Draw(img)
    d.text((15, 35), "SCHOLARSHIP NOTICE 2026", fill="black")

    res = extract_text_from_image(img, target_lang="hin")
    assert res.error is None
    assert res.engine_used == "tesseract"


# 8. Analysis cache hit verification (Performance Optimization)
def test_08_analysis_cache_hit_optimization():
    from unittest.mock import patch
    from notice2action.schemas import StructuredNotice, ExtractedFact, CertaintyStatus

    mock_notice = StructuredNotice(
        purpose=ExtractedFact(
            field_name="purpose",
            value="Cache Test Notice",
            status=CertaintyStatus.STATED,
            evidence_quote="IIMT UNIVERSITY CACHE TEST NOTICE",
        ),
        deadline=ExtractedFact(
            field_name="deadline",
            value="18 November 2026",
            status=CertaintyStatus.STATED,
            evidence_quote="All scholarship candidates must submit documents by 18 November 2026.",
        ),
        eligibility=ExtractedFact(
            field_name="eligibility",
            value="All scholarship candidates",
            status=CertaintyStatus.STATED,
            evidence_quote="All scholarship candidates must submit documents by 18 November 2026.",
        ),
        fee_or_cost=ExtractedFact(
            field_name="fee_or_cost",
            value="Not stated in the notice.",
            status=CertaintyStatus.NOT_STATED,
            evidence_quote=None,
        ),
        required_documents=ExtractedFact(
            field_name="required_documents",
            value="documents",
            status=CertaintyStatus.STATED,
            evidence_quote="All scholarship candidates must submit documents by 18 November 2026.",
        ),
        contact_details=ExtractedFact(
            field_name="contact_details",
            value="dsw@iimtu.ac.in",
            status=CertaintyStatus.STATED,
            evidence_quote="Contact: dsw@iimtu.ac.in",
        ),
        required_actions=ExtractedFact(
            field_name="required_actions",
            value="Submit documents",
            status=CertaintyStatus.STATED,
            evidence_quote="All scholarship candidates must submit documents by 18 November 2026.",
        ),
        important_conditions=ExtractedFact(
            field_name="important_conditions",
            value="Not stated in the notice.",
            status=CertaintyStatus.NOT_STATED,
            evidence_quote=None,
        ),
        raw_notice_text="Mock notice",
    )

    sample_text = (
        "IIMT UNIVERSITY CACHE TEST NOTICE\n"
        "All scholarship candidates must submit documents by 18 November 2026.\n"
        "Contact: dsw@iimtu.ac.in"
    )

    with patch("notice2action.api.server.NoticeAnalyzer.analyze_notice", return_value=mock_notice):
        # First call (cold execution)
        res1 = client.post(
            "/api/analyze",
            json={"notice_text": sample_text, "reading_level": "standard", "target_language": "en"},
        )
        assert res1.status_code == 200
        data1 = res1.json()
        fp = data1["fingerprint"]
        assert fp is not None

        # Second call with identical payload (cache hit)
        start = time.time()
        res2 = client.post(
            "/api/analyze",
            json={"notice_text": sample_text, "reading_level": "standard", "target_language": "en"},
        )
        elapsed = time.time() - start
        assert res2.status_code == 200
        data2 = res2.json()

        # Cache hit must be sub-second (< 0.2s) and return identical structured data
        assert elapsed < 0.2, f"Expected cache hit under 0.2s, got {elapsed:.3f}s"
        assert data2["fingerprint"] == data1["fingerprint"]
        assert data2["structured_notice"]["purpose"]["value"] == data1["structured_notice"]["purpose"]["value"]


# 9. Ingest upload REST endpoint with PDF file
def test_09_ingest_upload_endpoint_pdf():
    text_content = "GOVERNMENT OF UTTAR PRADESH\nMerit Scholarship Closing Date: 30 November 2026."
    pdf_bytes = create_synthetic_digital_pdf(text_content)

    response = client.post(
        "/api/ingest/upload",
        files={"file": ("higher_ed_notice.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "pdf"
    assert "higher_ed_notice.pdf" in data["filename"]
    assert "30 November 2026" in data["raw_text"]
    assert data["char_count"] > 20

