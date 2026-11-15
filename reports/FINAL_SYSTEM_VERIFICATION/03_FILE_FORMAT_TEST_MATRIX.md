# 03 — FILE FORMAT TEST MATRIX & INGESTION VERIFICATION
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Supported Document & Image Formats

The ingestion engine (`src/notice2action/ingestion.py` and `src/notice2action/ocr.py`) supports all required text, document, and image formats:

| Format Category | Extension | Extraction Engine | Multi-Page Support | Tested Status |
|---|---|---|---|---|
| **Plain Text** | `.txt` | Direct UTF-8 Stream Parser | Single/Multi-paragraph | **PASS** |
| **PDF Documents** | `.pdf` | PyMuPDF (`fitz`) Text Layer | Full Multi-Page Stream | **PASS** |
| **Scanned PDF** | `.pdf` | PyMuPDF + Tesseract OCR Fallback | Page-by-page OCR | **PASS** |
| **Microsoft Word** | `.docx` | Standard `zipfile` + XML `ElementTree` | Paragraphs & Headings | **PASS** |
| **PNG Image** | `.png` | PIL Image + Tesseract OCR | Grayscale / RGB | **PASS** |
| **JPEG Image** | `.jpg`, `.jpeg` | PIL Image + Tesseract OCR | Compressed Scans | **PASS** |
| **WebP Image** | `.webp` | PIL Image + Tesseract OCR | Modern Web Captures | **PASS** |
| **TIFF Image** | `.tif`, `.tiff` | PIL Image + Multi-Frame OCR | Single & Multi-Frame | **PASS** |
| **Legacy Word** | `.doc` | Rejected Safely (Requires conversion to .docx) | Explanatory Error | **PASS** |

---

## 2. Ingestion Validation & Security Handling

1. **Signature / Magic Byte Validation:** Uploaded files are inspected for true content types rather than relying blindly on file extensions.
2. **File Size Boundaries:** Max file size limit enforced (10MB for documents, 15MB for high-resolution scanned TIFF/PDFs).
3. **Safe Storage Paths:** Files are persisted to `data/documents/<uuid>_<filename>` using sanitized filenames that prevent directory traversal attacks (`../` stripped).
4. **Zero Macro Execution:** `.docx` files are parsed via pure XML element extraction (`word/document.xml`), neutralizing any embedded macros, scripts, or active content.
5. **OCR Degradation Handling:** Images with poor contrast, low DPI, or skew are preprocessed with auto-thresholding; if confidence is low, facts are flagged with `status="uncertain"` and `requires_confirmation=True`.
