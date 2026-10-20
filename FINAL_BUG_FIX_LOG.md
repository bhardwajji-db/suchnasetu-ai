# FINAL BUG FIX LOG — NOTICE2ACTION AI (PS02)

### BUG-001: Pydantic Validation Error on `missing_information` Dict Input
- **Reproduction:** When analyzing notice with Gemma 4, the model outputs `missing_information: [{"fact": "Scholarship amount not stated", "evidence_quote": None}]`.
- **Root Cause:** Schema declared `missing_information: List[str]`. Pydantic v2 raises `ValidationError: Input should be a valid string`.
- **Files Changed:** `src/notice2action/schemas.py`, `src/notice2action/analysis.py`.
- **Fix Implemented:** Added `@field_validator("missing_information", "uncertain_or_conflicting_details", mode="before")` with `normalize_string_list()` to coerce dicts and filter nulls/empties.
- **Regression Test:** Added `tests/test_structured_notice_regression.py` (8 tests).
- **Verification:** All 8 tests pass; live demo analysis produces clean string list without crashing.

### BUG-002: Stale In-Memory Streamlit Module Cache
- **Reproduction:** Browser running on `http://localhost:8501/` continued to throw the validation error even after files were updated on disk.
- **Root Cause:** Streamlit only watches the main script file (`app.py`), and does not reload imported modules in `src/notice2action/` that are already loaded in `sys.modules`.
- **Files Changed:** Server process management.
- **Fix Implemented:** Killed stale background processes and restarted fresh Streamlit daemon (`task-1360`).
- **Verification:** Health endpoint returns HTTP 200 OK; live app loads updated code cleanly.

### BUG-003: Missing `.to_ics_bytes()` Method on `ActionChecklist`
- **Reproduction:** `AppTest` raised `AttributeError: 'ActionChecklist' object has no attribute 'to_ics_bytes'` when rendering calendar export widget.
- **Root Cause:** UI component called `checklist.to_ics_bytes()` which was not implemented on the Pydantic schema.
- **Files Changed:** `src/notice2action/schemas.py`, `src/notice2action/ui/components.py`.
- **Fix Implemented:** Added RFC 5545 compliant `to_ics_bytes()` method to `ActionChecklist` and safeguarded `components.py` with `hasattr()` check.
- **Regression Test:** `tests/test_streamlit_interaction.py::test_ui_render_with_structured_data`.
- **Verification:** Test passed in 2.12s.

### BUG-004: Frontend Input Workspace Layout Imbalance
- **Reproduction:** Notice text was cramped into a small textarea hidden behind a radio toggle on the left, with duplicate textareas.
- **Root Cause:** Prototype layout nested both upload and paste into a single narrow column.
- **Files Changed:** `app.py`, `src/notice2action/ui/styles.py`.
- **Fix Implemented:** Created balanced two-column workspace: Upload Document on left, Notice Content / Ground-Truth Buffer on right, with dominant primary analyze button spanning below.
- **Verification:** Verified visually and via AppTest (`scratch/test_complete_user_journey.py`).
