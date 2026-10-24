# SYSTEM BUG & DEFECT REGISTER
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Inventory of Identified & Repaired Defects

| Bug ID | Severity | Reproduction Steps | Root Cause | Files Changed | Repair Description | Regression Test | Final Status |
|---|---|---|---|---|---|---|---|
| **BUG-01** | High | Run `npm run build` | Unused TypeScript imports (`SUPPORTED_LANGUAGES`, `LANGUAGE_CODES`) threw TS6133 errors | `frontend/src/i18n/index.ts` | Removed unused imports from index | `npm run build` (0 errors) | **RESOLVED** |
| **BUG-02** | High | Submit Q&A query on English notice | Localized static fallback answers overwrote valid English model responses | `src/notice2action/followup.py` | Preserved non-empty model responses before applying localized fallbacks | `tests/test_api_endpoints.py` | **RESOLVED** |
| **BUG-03** | Medium | Run live Gemma 4 test suite | Brittle substring assertion expected exact `"not specified"` instead of semantic `"does not specify"` | `tests/test_live_gemma4.py` | Updated assertion to accept semantic variants | `tests/test_live_gemma4.py` | **RESOLVED** |
| **BUG-04** | High | Run DB tests on Windows host | `[WinError 32]` when temp test directories were removed with open SQLite DB handles | `src/notice2action/storage/db.py` | Added explicit `close()` method to `DatabaseManager` and fixture teardown | `tests/test_storage_db.py` | **RESOLVED** |
| **BUG-05** | High | Upload document from temp folder | `path.relative_to(PROJECT_ROOT)` raised `ValueError` when file was outside project root | `src/notice2action/ingestion.py` | Wrapped relative path computation in safe `try-except` fallback | `tests/test_pdf_and_hindi_ocr_pipeline.py` | **RESOLVED** |
| **BUG-06** | High | Run language detection on Hindi | `HINDI_MARKERS` was undefined in script frequency evaluation, throwing NameError | `src/notice2action/language_detection.py` | Replaced with set operations on `HINDI_WORDS` and `MARATHI_WORDS` | `tests/test_hindi_ocr.py` | **RESOLVED** |
| **BUG-07** | High | Call `/api/demo-library/load` | `PROJECT_ROOT` was missing from `server.py` imports | `src/notice2action/api/server.py` | Added `PROJECT_ROOT` import from `notice2action.config` | `tests/test_demo_library_api.py` | **RESOLVED** |
| **BUG-08** | Medium | Edit source files with LF tools | Mixed CRLF line endings caused regex mismatch in AST / file editing tools | Multiple Python and TSX files | Normalized line endings to LF across source tree | Tool edits clean | **RESOLVED** |
| **BUG-09** | High | Run Demo 1 in synthetic suite | Applicant profile submitted `academic_year: int` causing Pydantic 422 Unprocessable Entity | `src/notice2action/schemas.py` | Added `ConfigDict(extra="allow")`, field aliases, and `model_validator` | `tests/test_synthetic_demo_suite.py` | **RESOLVED** |
| **BUG-10** | High | Evaluate eligibility in Demo 1 | Synthetic test expected `overall_verdict` attribute which was missing in response | `src/notice2action/schemas.py` | Added `overall_verdict: Optional[str]` and auto-populated from `overall_status` | `tests/test_synthetic_demo_suite.py` | **RESOLVED** |
| **BUG-11** | High | Run Corrigendum diff in Demo 3 | `RevisionEntry.category` did not enrich `change_category` to semantic names | `src/notice2action/schemas.py` | Enriched `sync_category` validator in `RevisionEntry` to map field deltas | `tests/test_synthetic_demo_suite.py` | **RESOLVED** |
| **BUG-12** | High | Run prompt injection Demo 5 | Assertion tested `raw_response_text`, which echoed the uploaded document in `raw_notice_text` | `tests/test_synthetic_demo_suite.py` | Stripped `raw_notice_text` input document before verifying model outputs | `tests/test_synthetic_demo_suite.py` | **RESOLVED** |
| **BUG-13** | Low | Run `start_all.bat` non-interactively | `timeout /t 4 /nobreak >nul` failed with `Input redirection is not supported` | `start_all.bat` | Replaced with non-interactive safe `ping -n 5 127.0.0.1 >nul` delay | `start_all.bat` execution | **RESOLVED** |
