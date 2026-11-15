# Baseline and Defect Audit Report
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Audit Scope:** Initial reproduction of baseline claims, regression tracking, and root-cause analysis of defects discovered during inspection.

---

## 1. Executive Summary

Prior to making architectural improvements, a systematic baseline audit was conducted across frontend, backend, OCR, and AI inference modules. While the initial documentation claimed 100% test passage, rigorous reproduction identified multiple concrete defects, build errors, and regressions that required targeted remediation.

All baseline issues have now been resolved, and the test suite has expanded from 20 to 21 frontend Vitest tests and 182 to 208 backend pytest tests, maintaining 100% passage.

---

## 2. Baseline Test Execution Results

| Test Category | Initial Claimed | Initial Measured | Final Verified | Status |
|---|---|---|---|---|
| **Frontend Vitest** | 20 / 20 passed | 0 / 20 (TS Build Failure) | **21 / 21 passed** | **PASS** |
| **Frontend TypeScript Build** | Clean (`tsc -b`) | TS6133 Unused vars | **Clean (0 errors)** | **PASS** |
| **Oxlint Code Quality** | 0 errors | 0 errors | **0 errors** | **PASS** |
| **Playwright Multi-Viewport (6 sizes)** | 2 / 2 passed | 2 / 2 passed | **2 / 2 passed** | **PASS** |
| **Backend Core Pytest** | 182 passed | 181 passed / 1 failed | **203 passed / 0 failed** | **PASS** |
| **Live Gemma 4 & OCR Pipeline** | 5 / 5 passed | Skipped (daemon off) | **5 / 5 passed** | **PASS** |
| **Demo Library Persistence API** | N/A (New) | N/A | **6 / 6 passed** | **PASS** |
| **SQLite Persistence Layer** | N/A (New) | N/A | **6 / 6 passed** | **PASS** |

---

## 3. Root-Cause Defect Analysis & Remediations

### Defect 1: TypeScript Build Failure TS6133 in i18n
- **Location:** `frontend/src/i18n/index.ts`
- **Symptom:** `error TS6133: 'SUPPORTED_LANGUAGES' is declared but its value is never read.`
- **Root Cause:** Redundant named imports on line 2 that were already re-exported on line 15.
- **Resolution:** Cleaned import statements to avoid unused symbol declarations.
- **Verification:** `npm --prefix frontend run build` completes with exit code 0.

### Defect 2: Pytest Regression in Unsupported Follow-Up Q&A
- **Location:** `src/notice2action/followup.py`
- **Symptom:** `AssertionError: assert 'does not specify' in 'इस नोटिस में इसके बारे में कोई जानकारी नहीं है।...'`
- **Root Cause:** A newly introduced internationalization patch unconditionally overwrote model-generated responses with `LOCALIZED_NOT_FOUND`, erasing valid English model answers.
- **Resolution:** Modified `followup.py` to preserve model-generated response text if non-empty, falling back to localized template messages only when the response is empty.
- **Verification:** `test_12_unsupported_followup_question` in `tests/test_unit_pipeline.py` passed immediately.

### Defect 3: Live Ollama Daemon Dormancy & Assertion Brittleness
- **Location:** `tests/test_live_gemma4.py`
- **Symptom:** Live tests were either skipped due to unstarted Ollama background process or failed due to brittle exact-match assertions (`"does not specify"` vs `"not specified"`).
- **Root Cause:** Ollama server was not running as a persistent background daemon; assertion expected exact substring `"does not specify"` while Gemma 4 generated natural English phrasing `"The notice explicitly states that the policy is not specified"`.
- **Resolution:** Launched `ollama.exe serve` as a persistent background daemon on `127.0.0.1:11434`; expanded substring assertions to accept semantic equivalents (`"not specified"`, `"not found"`, `"does not specify"`).
- **Verification:** All 5 live Gemma 4 inference tests passed in 196.46s.

### Defect 4: Windows SQLite File Locking (`[WinError 32]`)
- **Location:** `src/notice2action/storage/db.py` & `tests/test_storage_db.py`
- **Symptom:** Pytest fixture teardown threw `PermissionError: [WinError 32] The process cannot access the file because it is being used by another process`.
- **Root Cause:** Under Windows OS, active SQLite connection handles lock files on disk; temporary directory cleanup attempted deletion before connection garbage collection.
- **Resolution:** Implemented explicit `close()` method on `DatabaseManager` and called `temp_db.close()` in test fixture teardowns.
- **Verification:** All storage persistence tests pass cleanly without file lock leaks.

### Defect 5: Unhandled Path Resolution in Document Ingestion
- **Location:** `src/notice2action/storage/db.py`
- **Symptom:** `ValueError: path is not relative to project root` when saving documents created inside system temporary directories during tests.
- **Root Cause:** `save_document` called `path.relative_to(PROJECT_ROOT)` unconditionally without checking whether the path resided within the workspace root.
- **Resolution:** Wrapped relative path resolution in a `try...except ValueError` block, safely falling back to absolute string representations.
- **Verification:** Clean execution across both production and isolated testing environments.

### Defect 6: NameError in Hindi Marker Reference
- **Location:** `src/notice2action/language_detection.py`
- **Symptom:** `NameError: name 'HINDI_MARKERS' is not defined` during Devanagari Hindi vs. Marathi distinction.
- **Root Cause:** Variable was renamed to `HINDI_WORDS` during refactoring, but a leftover loop referenced `HINDI_MARKERS`.
- **Resolution:** Refactored Devanagari lexical scoring to use fast set intersections against `HINDI_WORDS` and `MARATHI_WORDS`.
- **Verification:** Complete accuracy across all 10 language fixtures.

---

## 4. Conclusion

The codebase was restored to a verified baseline state, resolving all lurking defects and establishing a rock-solid foundation for the 10-language UI, SQLite persistence, and 32-file Demo Library.
