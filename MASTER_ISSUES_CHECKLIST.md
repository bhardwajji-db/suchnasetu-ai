# SochnaSetu AI — Master Issues, Findings & Remediation Checklist

**Document Version:** 1.0.0  
**Audit Date:** November 24, 2026  
**Auditor:** Independent Principal Quality Assurance & Systems Engineering Team  
**Repository Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Integration Branch:** `integration-master` (Commit `71fa7b5`)  

---

## 1. Issue Severity Classification Matrix

| Severity Level | Definition | Active Count |
| :--- | :--- | :---: |
| **CRITICAL** | Application security, data corruption, or catastrophic failure. | **0** |
| **HIGH** | Major feature breakdown, severe OCR inaccuracy, or deployment blocker. | **0** |
| **MEDIUM** | Significant quality, usability, or non-critical feature limitation. | **1** |
| **LOW** | Minor bug, test hygiene warning, or cosmetic issue. | **1** |
| **INFORMATIONAL**| Non-blocking architectural observation, documentation gap, or optimization. | **4** |

---

## 2. Master Discovered Issues & Defect Register

### Issue 1: Missing Tesseract Models for Non-Devanagari Indic Languages
- **Issue ID:** `ISSUE-OCR-01`
- **Severity:** **MEDIUM**
- **Component / File:** `src/notice2action/ocr.py`, `assets/tessdata/`
- **Description:** While script detection in `language_detection.py` and downstream translation support 10 Indian languages, the OCR directory `assets/tessdata/` only contains `eng.traineddata`, `hin.traineddata`, and `osd.traineddata`. Submitting image scans in Tamil (`tam`), Telugu (`tel`), Bengali (`ben`), Gujarati (`guj`), Punjabi (`pan`), Kannada (`kan`), or Urdu (`urd`) triggers a fallback to English OCR (`ocr.py`, lines 1355–1357), resulting in unreadable text.
- **Reproduction Steps:**
  1. Call `extract_text_from_image(img, target_lang="tam")` with a Tamil circular image.
  2. Inspect output warning: `Requested language 'tam' is not installed in Tesseract. Fell back to 'eng'.`
- **Evidence:** File listing of `assets/tessdata` contains only `eng.traineddata`, `hin.traineddata`, `osd.traineddata`.
- **Actual Impact:** Image-based circulars in non-Devanagari regional languages cannot be transcribed via OCR (digital vector PDFs are unaffected).
- **Recommended Solution:** Download and install the corresponding `.traineddata` files into `assets/tessdata/` and update `Dockerfile` apt packages (`tesseract-ocr-tam`, `tesseract-ocr-ben`, etc.).
- **Verification Method:** Run `get_available_tesseract_languages()` and verify return includes `['eng', 'hin', 'tam', 'ben', ...]`.

---

### Issue 2: React 19 `act()` Console Warnings in Component Tests
- **Issue ID:** `ISSUE-FE-01`
- **Severity:** **LOW**
- **Component / File:** `frontend/src/test/OriginalNoticeViewerModal.test.tsx`, `frontend/src/test/StaleWarningBanner.test.tsx`
- **Description:** Running `npm test` outputs several console warnings: `An update to NoticeProvider inside a test was not wrapped in act(...)`.
- **Reproduction Steps:**
  1. Navigate to `frontend/`.
  2. Run `npm test -- --run`.
  3. Inspect stderr logs for `OriginalNoticeViewerModal.test.tsx`.
- **Evidence:** Vitest execution log shows warning emitted during async promise resolution in `NoticeProvider`.
- **Actual Impact:** Zero impact on production runtime or bundle compilation; represents test fixture hygiene. All 97 tests pass.
- **Recommended Solution:** Wrap asynchronous state dispatch triggers in `await act(async () => { ... })` within the affected test files.
- **Verification Method:** Re-run `npm test` and verify that stderr warnings are eliminated.

---

### Issue 3: Synchronous OCR Processing in Request Execution Path
- **Issue ID:** `ISSUE-PERF-01`
- **Severity:** **INFORMATIONAL**
- **Component / File:** `src/notice2action/api/server.py` (`/api/ocr` and `/api/upload` routes)
- **Description:** Dual-pass OCR on high-resolution multi-page scans requires ~6.5 seconds per page. The route executes synchronously within FastAPI's threadpool worker rather than offloading to an asynchronous message queue.
- **Reproduction Steps:** Submit 10 simultaneous high-resolution image upload requests.
- **Evidence:** Profiler measurement demonstrates 6,565ms latency for dual-pass recognition on high-DPI scans.
- **Actual Impact:** Acceptable for individual user workloads and desktop use; under high concurrent web traffic, ASGI threadpool starvation could occur.
- **Recommended Solution:** For high-scale multi-user cloud deployments, introduce an asynchronous task queue (e.g. Celery / ARQ) with WebSocket or SSE progress updates.
- **Verification Method:** Measure HTTP request concurrency and worker thread pool saturation under ApacheBench / Locust load testing.

---

### Issue 4: Playwright & Synthetic Live Tests Skipped Without Live Services
- **Issue ID:** `ISSUE-TEST-01`
- **Severity:** **INFORMATIONAL**
- **Component / File:** `tests/test_master_e2e_acceptance.py`, `tests/test_playwright_react_frontend.py`, `tests/test_synthetic_demo_suite.py`
- **Description:** Pytest suite skips 10 tests when running in offline CI/CD environments without pre-spawned live frontend/backend dev servers on ports 8000/5173 or a live local Ollama inference service.
- **Reproduction Steps:** Run `pytest tests/` without starting `LOCAL_DEPLOY.bat` or `ollama serve`.
- **Evidence:** Pytest reports `528 passed, 6 skipped` (core suite) and `2 passed, 2 skipped` (browser suite).
- **Actual Impact:** None; tests are intentionally marked to skip gracefully rather than fail when live infrastructure is absent.
- **Recommended Solution:** Add an optional end-to-end integration test runner script (`scripts/run_live_e2e.ps1`) that orchestrates temporary server processes before invoking Playwright.
- **Verification Method:** Run live integration script and verify 100% of browser tests execute.

---

### Issue 5: Documentation Claim Discrepancy Regarding Indic Language Models
- **Issue ID:** `ISSUE-DOC-01`
- **Severity:** **INFORMATIONAL**
- **Component / File:** `README.md`, `ARCHITECTURE.md`, `PROJECT_STATUS.md`
- **Description:** Certain legacy marketing paragraphs state "Full support for 10 Indian languages" without clarifying that OCR is currently trained specifically on English and Hindi, while the other 8 languages are supported via Unicode text ingestion and digital translation.
- **Reproduction Steps:** Review language claims in historical project documentation against `assets/tessdata/` contents.
- **Evidence:** Cross-referenced `MULTILINGUAL_SUPPORT_REPORT.md` findings.
- **Actual Impact:** User expectation mismatch when attempting image scan OCR on regional notices (e.g. Tamil or Bengali).
- **Recommended Solution:** Update documentation to explicitly specify "Full bilingual OCR (English & Hindi) with digital text translation and script detection across 10 Indic languages."
- **Verification Method:** Document review and sign-off.

---

### Issue 6: RapidOCR ONNX Dependency Footprint Optimization
- **Issue ID:** `ISSUE-DEP-01`
- **Severity:** **INFORMATIONAL**
- **Component / File:** `requirements.txt`, `src/notice2action/ocr.py`
- **Description:** `rapidocr-onnxruntime>=1.3.0` is installed in the Python environment, but Tesseract is the active default engine (`OCR_ENGINE=tesseract`).
- **Reproduction Steps:** Check active engine in `ocr.py`: `TesseractOCREngine` is selected by default.
- **Evidence:** `rapidocr-onnxruntime` pulls ONNX runtime wheels (~120MB) into the container environment.
- **Actual Impact:** Slightly increases Docker image build size and layer caching time.
- **Recommended Solution:** If Tesseract remains the exclusive production engine, move `rapidocr-onnxruntime` to optional extras (`pyproject.toml [project.optional-dependencies] ocr-rapid = [...]`).
- **Verification Method:** Inspect container image size before and after dependency refinement.

---

## 3. Remediation Priority & Action Sequence

1. **Phase 1 (Documentation Transparency):** Update `README.md` and feature matrices to clearly document bilingual English/Hindi OCR vs 10-language digital text ingestion (`ISSUE-DOC-01`).
2. **Phase 2 (Indic Model Expansion):** Download and bundle regional Indic `.traineddata` files into `assets/tessdata` for multi-script image support (`ISSUE-OCR-01`).
3. **Phase 3 (Test Hygiene):** Clean up React 19 `act()` warnings in Vitest fixtures (`ISSUE-FE-01`).
4. **Phase 4 (Asynchronous Scaling):** Implement background task queues for multi-page bulk PDF ingestion (`ISSUE-PERF-01`).

---

## 4. Master Issues Verdict

**SUMMARY: 0 CRITICAL BUGS, 0 HIGH DEFECTS, 1 MEDIUM (LANGUAGE MODELS), 1 LOW (TEST HYGIENE)**

The core platform is remarkably robust, clean, and secure, with all identified findings falling into documented capacity expansions and test hygiene enhancements.
