# 14 — KNOWN LIMITATIONS & ENVIRONMENT BOUNDARIES
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Document Format Boundaries
- **Legacy Microsoft Word (`.doc`):** Legacy binary `.doc` files (pre-2007 format) are rejected with a clear explanatory error prompting the user to convert the document to `.docx` or `.pdf`. This prevents reliance on deprecated, insecure COM automation or external cloud format conversion APIs.
- **Password-Protected / Encrypted PDFs:** PDFs protected by owner/user passwords cannot be decrypted without the password; an explanatory dialog asks the user to provide an unencrypted copy.

---

## 2. OCR Script Pack Dependencies
- Tesseract OCR relies on installed language traineddata (`eng.traineddata`, `hin.traineddata`, etc.) in `TESSDATA_PREFIX`.
- While English and Hindi OCR are fully bundled and verified, less common regional script scans (e.g. Punjabi Gurmukhi, Kannada) fall back gracefully to text extraction if the corresponding `.traineddata` file is not present on the host OS.

---

## 3. Local LLM Hardware Boundaries
- **Hardware Requirement:** Local inference via Ollama with `gemma4:latest` requires at least 8GB of system RAM (or 4GB+ dedicated VRAM for optimal speed).
- **Execution Speed:** On CPU-only environments, full notice extraction may take 30–60 seconds per long document.
- **Fail-Safe Mechanism:** When Ollama is offline or experiences memory pressure, the system automatically falls back to deterministic regex and heuristic fact extraction, ensuring zero service disruption.

---

## 4. Notification Transports
- **Telegram & Email Delivery:** External notification dispatch requires valid credentials in `.env` (`TELEGRAM_BOT_TOKEN`, `SMTP_HOST`). When unconfigured, reminders are preserved safely in SQLite and displayed via in-app notification banners.
