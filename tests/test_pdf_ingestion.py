"""
Comprehensive Test Suite for Secure PDF Ingestion in Notice2Action AI (PS02).
Tests born-digital PDF extraction, scanned PDF OCR fallback, security validations,
file corruption bounds, page limits, encryption rejection, and FastAPI endpoint contracts.
"""

import io
from pathlib import Path
import pytest
from pypdf import PdfWriter
from PIL import Image
from fastapi.testclient import TestClient

from notice2action.api.server import app
from notice2action.config import config
from notice2action.security import validate_uploaded_file, SecurityValidationError
from notice2action.ingestion import ingest_uploaded_file, extract_text_from_pdf


@pytest.fixture
def client():
    return TestClient(app)


def _create_sample_digital_pdf() -> bytes:
    """Creates a valid, syntactically conforming digital PDF with extractable notice text."""
    pdf_bytes = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 145 >>
stream
BT
/F1 12 Tf
72 712 Td
(OFFICIAL SCHOLARSHIP NOTICE: Submission deadline is 30 November 2026.) Tj
0 -20 Td
(All eligible applicants must submit verification forms to Room 204.) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000441 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
524
%%EOF"""
    return pdf_bytes


def _create_sample_scanned_pdf() -> bytes:
    """Creates a scanned PDF document containing an embedded image fixture."""
    fixture_path = Path("tests/fixtures/synthetic_notice_ocr.png")
    if not fixture_path.is_file():
        pytest.skip("synthetic_notice_ocr.png fixture not available.")
    pil_img = Image.open(fixture_path)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="PDF")
    return buffer.getvalue()


def test_digital_pdf_security_validation():
    """Verifies that a valid digital PDF passes security inspection and is typed as 'pdf'."""
    pdf_data = _create_sample_digital_pdf()
    safe_name, file_type = validate_uploaded_file("scholarship_notice.pdf", pdf_data)
    assert safe_name == "scholarship_notice.pdf"
    assert file_type == "pdf"


def test_digital_pdf_text_extraction():
    """Verifies born-digital text extraction from PDF without running OCR."""
    pdf_data = _create_sample_digital_pdf()
    text, is_scanned, note = extract_text_from_pdf(pdf_data)
    assert is_scanned is False
    assert "OFFICIAL SCHOLARSHIP NOTICE" in text
    assert "30 November 2026" in text
    assert "Room 204" in text


def test_digital_pdf_ingestion_result():
    """Verifies full ingestion pipeline for digital PDF."""
    pdf_data = _create_sample_digital_pdf()
    result = ingest_uploaded_file("notice.pdf", pdf_data)
    assert result.source_type == "pdf"
    assert result.error is None
    assert result.char_count > 50
    assert "30 November 2026" in (result.raw_text or "")


def test_scanned_pdf_ocr_extraction():
    """Verifies that a scanned PDF with no digital text routes through OCR correctly."""
    scanned_pdf = _create_sample_scanned_pdf()
    text, is_scanned, note = extract_text_from_pdf(scanned_pdf)
    assert is_scanned is True
    assert note is not None
    assert "Scanned PDF extracted via OCR" in note
    assert "SCHOLARSHIP NOTICE" in text.upper() or "UNIVERSITY" in text.upper()


def test_empty_pdf_rejection():
    """Verifies that a 0-byte file uploaded as PDF is rejected immediately."""
    with pytest.raises(SecurityValidationError, match="empty"):
        validate_uploaded_file("empty.pdf", b"")


def test_missing_magic_bytes_pdf_rejection():
    """Verifies rejection of files renamed to .pdf that lack the %PDF magic header."""
    fake_pdf = b"Plain text disguised as a PDF file."
    with pytest.raises(SecurityValidationError, match="%PDF signature"):
        validate_uploaded_file("fake.pdf", fake_pdf)


def test_corrupted_pdf_structure_rejection():
    """Verifies that corrupt PDF content starting with %PDF but containing invalid syntax is rejected."""
    corrupt_pdf = b"%PDF-1.4\nInvalid broken xref and missing trailer objects"
    with pytest.raises(SecurityValidationError, match="Corrupt or invalid PDF"):
        validate_uploaded_file("corrupt.pdf", corrupt_pdf)


def test_oversized_pdf_page_limit_rejection():
    """Verifies that PDFs exceeding max_pdf_pages are safely rejected to prevent DoS."""
    writer = PdfWriter()
    # Add pages exceeding limit
    for _ in range(config.max_pdf_pages + 5):
        writer.add_blank_page(width=100, height=100)
    buf = io.BytesIO()
    writer.write(buf)
    oversized_data = buf.getvalue()

    with pytest.raises(SecurityValidationError, match="exceeds maximum safety limit"):
        validate_uploaded_file("oversized.pdf", oversized_data)


def test_encrypted_pdf_rejection():
    """Verifies that password-encrypted PDFs are rejected with clear explanation."""
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.encrypt("secret_password")
    buf = io.BytesIO()
    writer.write(buf)
    encrypted_data = buf.getvalue()

    with pytest.raises(SecurityValidationError, match="Encrypted or password-protected"):
        validate_uploaded_file("encrypted.pdf", encrypted_data)


def test_api_upload_endpoint_digital_pdf(client):
    """Verifies the /api/ingest/upload endpoint with a digital PDF."""
    pdf_data = _create_sample_digital_pdf()
    files = {"file": ("scholarship_circular.pdf", pdf_data, "application/pdf")}
    resp = client.post("/api/ingest/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["source_type"] == "pdf"
    assert data["filename"] == "scholarship_circular.pdf"
    assert "30 November 2026" in data["raw_text"]
    assert data["char_count"] > 50
    assert len(data["fingerprint"]) == 64


def test_api_upload_endpoint_corrupt_pdf(client):
    """Verifies the /api/ingest/upload endpoint rejects corrupt PDF with HTTP 400."""
    files = {"file": ("broken.pdf", b"not-a-pdf", "application/pdf")}
    resp = client.post("/api/ingest/upload", files=files)
    assert resp.status_code == 400
    assert "PDF" in resp.json()["detail"]
