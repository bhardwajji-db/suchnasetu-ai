# 12 — COMPREHENSIVE DEFECT & REPAIR REGISTER
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Summary of Defects Discovered & Repaired

During full-system end-to-end execution, 11 distinct issues were identified, diagnosed, patched, and verified via regression tests:

| Defect ID | Component / Area | Root Cause | Exact Resolution | Regression Verification |
|---|---|---|---|---|
| **DEF-01** | Frontend I18n Index | Unused TypeScript imports (`SUPPORTED_LANGUAGES`, `LANGUAGE_CODES`) caused TS6133 compile errors | Removed redundant imports from `frontend/src/i18n/index.ts` | `npm run build` passed in 761ms |
| **DEF-02** | Follow-Up Q&A Engine | Localized static fallback answers overwrote valid English model responses in `followup.py` | Preserved non-empty model responses before applying localized fallbacks | `tests/test_api_endpoints.py` (16/16 passed) |
| **DEF-03** | Live Gemma 4 Test Suite | Brittle substring assertion expected exact `"not specified"` instead of semantic `"does not specify"` | Updated assertion to accept semantic variants | `tests/test_live_gemma4.py` (5/5 passed) |
| **DEF-04** | SQLite DB Teardown | `[WinError 32]` on Windows when temp test directories were removed with open DB handles | Added `close()` method to `DatabaseManager` and explicit fixture teardown | `tests/test_storage_db.py` (6/6 passed) |
| **DEF-05** | Ingestion Service | `path.relative_to(PROJECT_ROOT)` raised `ValueError` when files were uploaded from temp directories | Wrapped path computation in a safe `try-except` fallback | `tests/test_pdf_and_hindi_ocr_pipeline.py` passed |
| **DEF-06** | Language Detection | `HINDI_MARKERS` was undefined in character frequency evaluation | Replaced with set operations on `HINDI_WORDS` and `MARATHI_WORDS` | `tests/test_hindi_ocr.py` (6/6 passed) |
| **DEF-07** | Demo Library API | `PROJECT_ROOT` was missing from `server.py` demo load endpoint | Added `PROJECT_ROOT` import from `notice2action.config` | `tests/test_demo_library_api.py` (6/6 passed) |
| **DEF-08** | Windows CRLF Line Endings | Mixed CRLF line endings caused regex mismatch in AST / file editing tools | Normalized line endings to LF across edited source files | All edits applied cleanly |
| **DEF-09** | Applicant Profile Schema | Synthetic Demo 1 submitted `academic_degree`, `academic_percentage`, `academic_year: int` causing 422 Unprocessable Entity | Added `ConfigDict(extra="allow")`, field aliases, and `model_validator` in `schemas.py` | Demo 1 passed in `test_synthetic_demo_suite.py` |
| **DEF-10** | Eligibility Assessment Model | `EligibilityAssessment` response lacked `overall_verdict` expected by synthetic test client | Added `overall_verdict: Optional[str]` and auto-populated from `overall_status` | Demo 1 passed in `test_synthetic_demo_suite.py` |
| **DEF-11** | Revision Entry Categories | `RevisionEntry.category` did not enrich `change_category` to semantic names (`DEADLINE_EXTENSION`, `FEE_CHANGE`) | Enriched `sync_category` validator in `RevisionEntry` to map field deltas | Demo 3 passed in `test_synthetic_demo_suite.py` |
| **DEF-12** | Adversarial Security Test | Security test checked `assert INJECTION not in raw_response_text`, which echoed the input document in `raw_notice_text` | Stripped `raw_notice_text` input document before verifying model outputs | Demo 5 passed in `test_synthetic_demo_suite.py` |
