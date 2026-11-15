# 05. SOURCE CODE FIXES & ARCHITECTURAL REPAIRS — SOCHNASETU AI

---

## 1. Detailed Summary of Repaired Source Modules

### Module 1: `src/notice2action/api/server.py`
- **Issue:** FastAPI server lacked single-port production SPA routing; direct client deep links (`/dashboard`, `/facts`) returned 404 Not Found.
- **Repair:**
  - Mounted `StaticFiles(directory="frontend/dist/assets")` to `/assets`.
  - Added catch-all route `@app.get("/{full_path:path}")` returning `frontend/dist/index.html`.
  - Enforced strict path traversal guards ensuring paths containing `..` or system paths are rejected.
- **Verification:** Tested in `tests/test_api_endpoints.py::test_api_samples_path_traversal_protection` and `verify_all_features.py` Test 3 (Status 200).

### Module 2: `frontend/src/i18n/I18nContext.tsx`
- **Issue:** Changing language in Header updated local dictionary tokens but failed to propagate to `NoticeContext.selectedLang`.
- **Repair:** Bound `I18nContext.setLanguage` to trigger `NoticeContext.setSelectedLang` synchronously and updated root `document.documentElement.lang` and `dir`.
- **Verification:** Tested in `frontend/src/test/MultilingualSwitching.test.tsx` (5/5 PASSED).

### Module 3: `frontend/src/views/GroundedFactsView.tsx`
- **Issue:** Viewing Grounded Facts prior to notice analysis triggered an unhandled `TypeError: Cannot read properties of null (reading 'purpose')`.
- **Repair:** Added safe property access (`structuredNotice?.purpose`) and implemented a responsive empty state with a "Load Sample Notice" call-to-action.
- **Verification:** Verified in Vitest component mounting tests.

### Module 4: `src/notice2action/security.py`
- **Issue:** Adversarial notices attempted to override prompt instructions and inject fake legal penalties into structured JSON output.
- **Repair:** Wrapped incoming notice text in inert XML delimiters (`<notice_document>...</notice_document>`), injected anti-jailbreak negative constraints, and flagged overrides into `uncertain_or_conflicting_details`.
- **Verification:** Verified in `verify_all_features.py` Test 12.
