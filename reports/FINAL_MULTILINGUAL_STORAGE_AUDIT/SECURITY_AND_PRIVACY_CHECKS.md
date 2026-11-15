# Security, Privacy & Local-First Verification
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Scope:** Offline boundaries, telemetry inspection, sanitization, path traversal defenses, zip-slip validation, and prompt injection hardening.

---

## 1. Zero Cloud Telemetry & 100% Local Inference

A defining tenet of SochnaSetu AI is citizen privacy. In government welfare, legal disputes, scholarship applications, and municipal circulars, citizens often process sensitive personal documents.

### Local-First Architecture Audit:
- **Model Inference:** 100% hosted on `127.0.0.1:11434` (Ollama `gemma4:latest`).
- **OCR Engine:** 100% offline local Tesseract binaries in `assets/tessdata/`.
- **Database Engine:** Local file-based SQLite database in `data/suchnasetu.db`.
- **Network Boundaries:** Zero external outbound telemetry, tracking scripts, third-party analytics, or paid cloud APIs. All communications terminate at `localhost` / `127.0.0.1`.

---

## 2. Ingestion & Storage Defenses

| Threat Vector | Mitigation Strategy | Verification Test | Result |
|---|---|---|:---:|
| **Path Traversal (Zip-Slip)** | In DOCX extraction, every zip entry path is validated to ensure it does not escape the extraction directory using `os.path.commonpath`. | Attempted upload of `../../malicious.xml` inside docx archive | **BLOCKED** |
| **Path Traversal in Filesystem** | Filenames sanitized via `secure_filename()`; relative path resolution wrapped in safety guards. | Upload of file named `../../../etc/passwd` | **BLOCKED** |
| **Decompression Bomb** | Pillow `Image.MAX_IMAGE_PIXELS` set to safe threshold (89,478,485 pixels). | 100000x100000 synthetic pixel image | **REJECTED** |
| **Executable Renaming** | Binary magic-byte sniffing verifies genuine PDF (`%PDF`), PNG (`\x89PNG`), TIFF (`II*`), and JPEG headers. | `.exe` renamed to `.pdf` | **REJECTED** |
| **SQL Injection** | Parametrized SQLite queries used exclusively across all database adapters in `src/notice2action/storage/db.py`. | Input `' OR '1'='1` in search fields | **SANITIZED** |
| **XSS & Script Execution** | React JSX escaping prevents execution of embedded script tags in notice HTML views. | Notice containing `<script>alert(1)</script>` | **ESCAPED** |

---

## 3. Adversarial Prompt Injection Hardening

Civic notices can be targeted by adversarial prompt injections intended to confuse LLM summaries (e.g. fraudulent relief cancellation orders).

- **Defense-in-Depth:**
  1. System prompt strictly bounds the assistant to document-grounded facts.
  2. The LLM is explicitly forbidden from following instructions contained *inside* the notice text.
  3. Verbatim quotes must match indexed document tokens in `EvidenceService`.
- **Verification:** Scenario 5 (`tests/test_synthetic_demo_suite.py::test_demo_05_adversarial_injection`) passed with 100% rejection of injected override instructions.
