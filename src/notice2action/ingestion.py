"""
Notice Ingestion Module for SuchnaSetu AI.
Handles user inputs from text pasting or file uploads safely.
Supports PDF (digital and scanned via OCR), images (PNG, JPG, WEBP, TIFF),
plain text (TXT), and Word documents (DOCX).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List
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
    source_type: str  # "text" | "image" | "pdf" | "docx"
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
    if not clean_text:
        return IngestionResult(
            source_type="text",
            filename=None,
            raw_text=None,
            image=None,
            error="Notice text contains only unprintable or invalid characters.",
        )

    warning = detect_prompt_injection(clean_text)

    return IngestionResult(
        source_type="text",
        filename="pasted_notice.txt",
        raw_text=clean_text,
        image=None,
        security_warning=warning,
        char_count=len(clean_text),
    )


def _render_pdf_page_pdftoppm(file_bytes: bytes, page_idx: int, dpi: int = 300) -> Optional[Image.Image]:
    """Renders a single PDF page at configurable DPI using pdftoppm if installed."""
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = Path(tmpdir) / "doc.pdf"
        pdf_path.write_bytes(file_bytes)
        out_prefix = Path(tmpdir) / "page"
        cmd = [
            pdftoppm,
            "-png",
            "-r", str(dpi),
            "-f", str(page_idx),
            "-l", str(page_idx),
            str(pdf_path),
            str(out_prefix),
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
            if res.returncode == 0:
                rendered_files = sorted(Path(tmpdir).glob("page-*.png"))
                if rendered_files:
                    img = Image.open(rendered_files[0]).convert("RGB")
                    img.load()
                    return img
        except Exception:
            pass
    return None


def extract_text_from_pdf(file_bytes: bytes, target_lang: str = "eng+hin") -> Tuple[str, bool, Optional[str]]:
    """
    Extracts text from PDF documents:
    1. First attempts high-fidelity digital text extraction via pypdf page by page.
    2. If a page has no or very sparse digital text (< 30 characters), renders page at
       configurable resolution (default 300 DPI) via pdftoppm or extracts embedded page images.
    3. Seamlessly joins all pages, keeping digital text where available and OCR text for scanned pages.
    Returns: (extracted_text, is_scanned_pdf, informational_note)
    """
    import pypdf
    from notice2action.ocr import extract_text_from_image
    from notice2action.config import config

    reader = pypdf.PdfReader(BytesIO(file_bytes))
    page_texts: List[str] = []
    scanned_pages_found = 0
    digital_pages_found = 0

    for idx, page in enumerate(reader.pages, 1):
        p_text = ""
        try:
            p_text = (page.extract_text() or "").strip()
        except Exception:
            p_text = ""

        # If page has substantial digital text, preserve directly
        if len(p_text) >= 30:
            digital_pages_found += 1
            page_texts.append(p_text)
            continue

        # If digital text is missing or sparse, inspect page scans for OCR fallback
        page_ocr_parts: List[str] = []
        rendered_page = _render_pdf_page_pdftoppm(file_bytes, idx, dpi=getattr(config, "pdf_raster_dpi", 300))
        if rendered_page:
            try:
                ocr_res = extract_text_from_image(rendered_page, target_lang=target_lang)
                if ocr_res.extracted_text and ocr_res.extracted_text.strip():
                    page_ocr_parts.append(ocr_res.extracted_text.strip())
            except Exception:
                pass
        else:
            try:
                for img_idx, img_obj in enumerate(page.images):
                    pil_img = Image.open(BytesIO(img_obj.data)).convert("RGB")
                    ocr_res = extract_text_from_image(pil_img, target_lang=target_lang)
                    if ocr_res.extracted_text and ocr_res.extracted_text.strip():
                        page_ocr_parts.append(ocr_res.extracted_text.strip())
            except Exception:
                pass

        if page_ocr_parts:
            scanned_pages_found += 1
            ocr_combined = "\n".join(page_ocr_parts)
            # Prepend page marker if multi-page
            if len(reader.pages) > 1:
                page_texts.append(f"--- Page {idx} ---\n{ocr_combined}")
            else:
                page_texts.append(ocr_combined)
        elif p_text:
            # Fallback to whatever short digital text was present
            digital_pages_found += 1
            page_texts.append(p_text)

    full_text = "\n\n".join(page_texts).strip()

    if not full_text:
        raise ValueError("The uploaded PDF contains no extractable digital text and no readable page scans.")

    is_scanned = scanned_pages_found > 0
    info_note = (
        f"Scanned PDF extracted via OCR ({scanned_pages_found} page scan(s))."
        if is_scanned
        else None
    )

    return full_text, is_scanned, info_note


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Safely extracts full text content from a .docx file including:
    - Headers (word/header*.xml)
    - Body paragraphs, tables, line breaks, and tabs (word/document.xml)
    - Footers (word/footer*.xml)
    Protects against XXE and decompression attacks.
    """
    import zipfile
    import xml.etree.ElementTree as ET
    from io import BytesIO

    with zipfile.ZipFile(BytesIO(file_bytes)) as zf:
        namelist = zf.namelist()
        if "word/document.xml" not in namelist:
            raise ValueError("The uploaded DOCX file is missing 'word/document.xml'.")

        def _extract_paragraph_text(p_elem, ns: str) -> str:
            parts = []
            for child in p_elem.iter():
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if child_tag == "t" and child.text:
                    parts.append(child.text)
                elif child_tag in ("br", "cr"):
                    parts.append("\n")
                elif child_tag == "tab":
                    parts.append("\t")
            return "".join(parts)

        def _parse_xml_element(xml_bytes: bytes) -> List[str]:
            # XXE defense: check for external entity declarations
            if b"<!DOCTYPE" in xml_bytes and (b"SYSTEM" in xml_bytes or b"ENTITY" in xml_bytes):
                raise ValueError("DOCX contains potentially malicious XML external entity references.")

            tree = ET.fromstring(xml_bytes)
            ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            lines = []

            # Locate document body or root
            body = tree.find(f"{{{ns}}}body")
            elements_to_scan = body if body is not None else tree

            for elem in elements_to_scan:
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                if tag == "p":
                    p_text = _extract_paragraph_text(elem, ns)
                    if p_text.strip():
                        lines.append(p_text.strip())
                elif tag == "tbl":
                    # Iterate rows and cells
                    for row in elem.iter(f"{{{ns}}}tr"):
                        cell_texts = []
                        for cell in row.iter(f"{{{ns}}}tc"):
                            cell_parts = []
                            for cp in cell.iter(f"{{{ns}}}p"):
                                cpt = _extract_paragraph_text(cp, ns)
                                if cpt.strip():
                                    cell_parts.append(cpt.strip())
                            cell_texts.append(" ".join(cell_parts).strip())
                        if any(cell_texts):
                            lines.append(" | ".join(cell_texts))
            return lines

        doc_lines: List[str] = []

        # 1. Header XML files (e.g. letterheads, reference numbers, dates)
        header_files = sorted(n for n in namelist if n.startswith("word/header") and n.endswith(".xml"))
        for h_name in header_files:
            try:
                doc_lines.extend(_parse_xml_element(zf.read(h_name)))
            except Exception:
                pass

        # 2. Main Document Body
        body_lines = _parse_xml_element(zf.read("word/document.xml"))
        doc_lines.extend(body_lines)

        # 3. Footer XML files
        footer_files = sorted(n for n in namelist if n.startswith("word/footer") and n.endswith(".xml"))
        for f_name in footer_files:
            try:
                doc_lines.extend(_parse_xml_element(zf.read(f_name)))
            except Exception:
                pass

    full_text = "\n\n".join(doc_lines).strip()
    if not full_text:
        raise ValueError("The uploaded DOCX document contains no text.")
    return full_text


def ingest_uploaded_file(file_name: str, file_bytes: bytes) -> IngestionResult:
    """
    Safely ingests an uploaded file (image, text, PDF, or DOCX).
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
            # Try utf-8-sig/utf-8 first, fallback to cp1252/latin-1
            text = None
            for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
                try:
                    text = file_bytes.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                text = file_bytes.decode("latin-1", errors="replace")

            clean_text = sanitize_input_text(text)
            if not clean_text:
                return IngestionResult(
                    source_type="text",
                    filename=safe_name,
                    raw_text=None,
                    image=None,
                    error="Uploaded text file contains no readable text content.",
                )

            warning = detect_prompt_injection(clean_text)
            return IngestionResult(
                source_type="text",
                filename=safe_name,
                raw_text=clean_text,
                image=None,
                security_warning=warning,
                char_count=len(clean_text),
            )
        except Exception as e:
            return IngestionResult(
                source_type="text",
                filename=safe_name,
                raw_text=None,
                image=None,
                error=f"Failed to process text file: {e}",
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

    elif file_type == "docx":
        try:
            docx_text = extract_text_from_docx(file_bytes)
            clean_text = sanitize_input_text(docx_text)
            warning = detect_prompt_injection(clean_text)
            return IngestionResult(
                source_type="docx",
                filename=safe_name,
                raw_text=clean_text,
                image=None,
                security_warning=warning,
                char_count=len(clean_text),
            )
        except Exception as e:
            return IngestionResult(
                source_type="docx",
                filename=safe_name,
                raw_text=None,
                image=None,
                error=f"Failed to process DOCX: {e}",
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
