"""
Notice Ingestion Module for SuchnaSetu AI.
Handles user inputs from text pasting or file uploads safely.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
from io import BytesIO
from PIL import Image

from notice2action.security import (
    validate_uploaded_file,
    sanitize_input_text,
    detect_prompt_injection,
    SecurityValidationError,
)


@dataclass
class IngestionResult:
    source_type: str  # "text" | "image"
    filename: Optional[str]
    raw_text: Optional[str]
    image: Optional[Image.Image]
    security_warning: Optional[str] = None
    char_count: int = 0
    error: Optional[str] = None


def ingest_pasted_text(pasted_text: str) -> IngestionResult:
    """Safely ingests and sanitizes directly entered text."""
    if not pasted_text or not pasted_text.strip():
        return IngestionResult(
            source_type="text",
            filename=None,
            raw_text=None,
            image=None,
            error="Notice text is empty. Please paste or enter the notice text.",
        )

    clean_text = sanitize_input_text(pasted_text)
    warning = detect_prompt_injection(clean_text)

    return IngestionResult(
        source_type="text",
        filename="pasted_notice.txt",
        raw_text=clean_text,
        image=None,
        security_warning=warning,
        char_count=len(clean_text),
    )


def extract_text_from_pdf(file_bytes: bytes, target_lang: str = "eng+hin") -> Tuple[str, bool, Optional[str]]:
    """
    Extracts text from PDF documents:
    1. First attempts high-fidelity digital text extraction via pypdf.
    2. If text is sparse or absent (< 30 characters), extracts embedded page images and executes Tesseract OCR.
    Returns: (extracted_text, is_scanned_pdf, informational_note)
    """
    import pypdf
    from notice2action.ocr import extract_text_from_image

    reader = pypdf.PdfReader(BytesIO(file_bytes))
    digital_parts = []
    for idx, page in enumerate(reader.pages, 1):
        try:
            p_text = page.extract_text() or ""
            if p_text.strip():
                digital_parts.append(p_text.strip())
        except Exception:
            pass

    full_digital = "\n\n".join(digital_parts).strip()
    if len(full_digital) >= 30:
        return full_digital, False, None

    # Fallback: Extract embedded page scans and perform adaptive OCR
    ocr_parts = []
    scanned_pages_found = 0
    for idx, page in enumerate(reader.pages, 1):
        try:
            for img_idx, img_obj in enumerate(page.images):
                scanned_pages_found += 1
                pil_img = Image.open(BytesIO(img_obj.data)).convert("RGB")
                ocr_res = extract_text_from_image(pil_img, target_lang=target_lang)
                if ocr_res.extracted_text and ocr_res.extracted_text.strip():
                    ocr_parts.append(f"--- Page {idx} ---\n{ocr_res.extracted_text.strip()}")
        except Exception:
            pass

    full_ocr = "\n\n".join(ocr_parts).strip()
    if full_ocr:
        return full_ocr, True, f"Scanned PDF extracted via OCR ({scanned_pages_found} page scan(s))."

    if full_digital:
        return full_digital, False, None

    raise ValueError("The uploaded PDF contains no extractable digital text and no readable page scans.")


def ingest_uploaded_file(file_name: str, file_bytes: bytes) -> IngestionResult:
    """
    Safely ingests an uploaded file (image, text, or PDF).
    Validates file bounds, format integrity, and detects malicious patterns.
    """
    try:
        safe_name, file_type = validate_uploaded_file(file_name, file_bytes)
    except SecurityValidationError as e:
        return IngestionResult(
            source_type="unknown",
            filename=file_name,
            raw_text=None,
            image=None,
            error=str(e),
        )

    if file_type == "text":
        try:
            text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text = file_bytes.decode("latin-1", errors="replace")
        clean_text = sanitize_input_text(text)
        warning = detect_prompt_injection(clean_text)
        return IngestionResult(
            source_type="text",
            filename=safe_name,
            raw_text=clean_text,
            image=None,
            security_warning=warning,
            char_count=len(clean_text),
        )
    elif file_type == "pdf":
        try:
            pdf_text, is_scanned, warning_note = extract_text_from_pdf(file_bytes)
            clean_text = sanitize_input_text(pdf_text)
            warning = detect_prompt_injection(clean_text)
            combined_warning = f"{warning_note}. {warning}" if (warning_note and warning) else (warning_note or warning)
            return IngestionResult(
                source_type="pdf",
                filename=safe_name,
                raw_text=clean_text,
                image=None,
                security_warning=combined_warning,
                char_count=len(clean_text),
            )
        except Exception as e:
            return IngestionResult(
                source_type="pdf",
                filename=safe_name,
                raw_text=None,
                image=None,
                error=f"Failed to process PDF: {e}",
            )
    elif file_type == "image":
        try:
            img = Image.open(BytesIO(file_bytes)).convert("RGB")
            return IngestionResult(
                source_type="image",
                filename=safe_name,
                raw_text=None,
                image=img,
                security_warning=None,
                char_count=0,
            )
        except Exception as e:
            return IngestionResult(
                source_type="image",
                filename=safe_name,
                raw_text=None,
                image=None,
                error=f"Failed to process image: {e}",
            )

    return IngestionResult(
        source_type="unknown",
        filename=safe_name,
        raw_text=None,
        image=None,
        error="Unknown file type encountered.",
    )
