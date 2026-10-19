"""
Notice Ingestion Module for Notice2Action AI.
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


def ingest_uploaded_file(file_name: str, file_bytes: bytes) -> IngestionResult:
    """
    Safely ingests an uploaded file (image or text).
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
