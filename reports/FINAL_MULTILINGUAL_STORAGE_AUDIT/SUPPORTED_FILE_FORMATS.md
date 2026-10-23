# Supported File Formats Policy & Ingestion Verification
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Scope:** Ingestion pipeline, format validation, parsing engines, security boundaries, and rejection of malformed inputs.

---

## 1. Supported Formats Policy

SochnaSetu AI enforces a strict, documented file ingestion policy. Renaming an invalid file does not bypass detection; actual binary magic bytes and MIME structures are verified before extraction begins.

| Extension | Category | Ingestion Method | Multi-page Support | Max Size Limit | Security Protections |
|---|---|---|:---:|:---:|---|
| `.txt` | Plain Text | UTF-8 / UTF-16 decoding with fallback | Yes | 10 MB | Normalized whitespace, stripped control bytes |
| `.pdf` | Digital PDF | `pypdf` + `fitz` text extraction | Yes (up to 50 pages) | 25 MB | Decompressed stream limits, no JS execution |
| `.pdf` | Scanned PDF | Page-by-page rendering + Tesseract OCR | Yes (up to 10 pages) | 25 MB | Memory-bounded rasterization, timeout limits |
| `.docx` | Word Document | Office Open XML parser (`zipfile` + `ET`) | Yes | 15 MB | Zip-slip protection, macro rejection (`.docm` blocked) |
| `.png` | Raster Image | Contrast enhancement + Tesseract OCR | Single page | 15 MB | Decompression bomb limits (`MAX_IMAGE_PIXELS`) |
| `.jpg` / `.jpeg` | Raster Image | EXIF orientation fix + Tesseract OCR | Single page | 15 MB | Decompression bomb limits |
| `.webp` | Web Image | PIL decoding + Tesseract OCR | Single page | 15 MB | Validated RIFF WebP header |
| `.tif` / `.tiff` | Scanned Image | Multi-frame TIFF reader + Tesseract OCR | Yes (multi-frame) | 25 MB | Validated TIFF endian headers (`II` / `MM`) |

---

## 2. Technical Ingestion Implementations

### 2.1 DOCX Ingestion Without External Dependencies
To avoid heavy third-party dependencies (`python-docx`), SochnaSetu AI implements a lightweight, native Office Open XML extractor:
1. Opens the file as a standard Python `zipfile.ZipFile`.
2. Validates zip entry paths to block path traversal (Zip-Slip) attacks.
3. Locates and streams `word/document.xml`.
4. Parses XML nodes using `xml.etree.ElementTree`, extracting paragraphs (`<w:p>`) and table cells (`<w:tc>`) while preserving document flow and paragraph breaks.

### 2.2 Scanned & Image OCR Pipeline
1. **Magic Byte Verification:**
   - PNG: `\x89PNG\r\n\x1a\n`
   - JPEG: `\xff\xd8\xff`
   - WebP: `RIFF....WEBP`
   - TIFF: `II*\x00` (little-endian) or `MM\x00*` (big-endian)
2. **Image Preprocessing:**
   - Auto-rotation based on EXIF tag 274.
   - Grayscale conversion and Otsu dynamic contrast thresholding.
   - Bilateral noise filtering for degraded civic circular scans.
3. **OCR Engine:**
   - Tesseract OCR (`tesseract.exe`) targeting installed language packs (`eng`, `hin`, `osd`).
   - For other regional scripts, the system leverages digital text extraction or presents honest capability boundaries rather than fabricating ungrounded OCR text.

---

## 3. Error Handling and Edge Cases

The ingestion engine was verified against corrupt, empty, malformed, and adversarial files:

| Edge Case Test | Test Input | Expected Behavior | Measured Result |
|---|---|---|---|
| **Empty File** | 0-byte `.txt` or `.pdf` | HTTP 422: Notice text cannot be empty | PASS: Safely rejected |
| **Renamed Executable** | `.exe` renamed to `.pdf` | Magic byte mismatch rejection | PASS: Rejected as invalid PDF |
| **Zip Bomb / Oversized** | Nested compressed zip | Max decompress ratio check | PASS: Safely terminated |
| **Encrypted / Password PDF** | Protected circular | Clear user message: "Password protected PDF" | PASS: Honest error returned |
| **Corrupt Image** | Truncated JPEG stream | Pillow `UnidentifiedImageError` caught | PASS: HTTP 400 error returned |
| **Macro Document** | Word `.docm` with VBA | Rejected by file format policy | PASS: Blocked |
