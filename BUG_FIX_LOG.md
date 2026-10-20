# BUG FIX LOG — NOTICE2ACTION AI (PS02)

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
- **Verification:** Verified fresh code execution via HTTP 200 health probe and AppTest.

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

### BUG-005: Sandboxed Iframe Tab Navigation Dispatch Failure
- **Reproduction:** Clicking sidebar buttons failed to switch tabs in the main dashboard area.
- **Root Cause:** Custom HTML injected via `st.components.v1.html` runs inside sandboxed iframes blocking access to `window.parent.document`. Streamlit 1.66 also switched to React Aria tabs (`div[role="tab"]`), breaking BaseWeb selectors.
- **Files Changed:** `app.py`, `src/notice2action/ui/styles.py`.
- **Fix Implemented:** Migrated to native dynamic tab keying (`f"main_dashboard_tabs_{cur_tab_idx}"`) with `on_click=set_active_tab` callbacks.
- **Verification:** Verified via Playwright in real headless Chrome (`tests/test_playwright_e2e.py`).

### BUG-006: StreamlitWidgetAlreadyInstantiatedError on Navigation
- **Reproduction:** Clicking sidebar nav buttons crashed the application with widget instantiation error.
- **Root Cause:** Modifying `st.session_state` keys during script body execution after `st.tabs` creation.
- **Files Changed:** `app.py`.
- **Fix Implemented:** Switched all nav buttons to pre-instantiation `on_click` callbacks executing before the script body evaluates.
- **Verification:** Verified via `tests/test_ui_controls_comprehensive.py`.

### BUG-007: Suggested Q&A Lifecycle Input Overwrite
- **Reproduction:** Clicking preset questions in Tab 4 cleared the input text or triggered premature empty submission.
- **Root Cause:** Widget state lifecycle overwrite during rerun.
- **Files Changed:** `app.py`.
- **Fix Implemented:** Added module-level `set_qa_inquiry()` callback and fallback evaluation on `(user_q or st.session_state.get('qa_input_text_box', ''))`.
- **Verification:** Verified in Playwright E2E and `test_ui_controls_comprehensive.py`.

### BUG-008: Stale Structured Notice State After Buffer Modification
- **Reproduction:** Modifying text buffer after running analysis showed outdated facts, summaries, and checklists without indication.
- **Root Cause:** No cryptographic binding between buffer contents and cached analysis results.
- **Files Changed:** `app.py`, `tests/test_notice_fingerprint_stale.py`.
- **Fix Implemented:** Implemented SHA-256 fingerprint comparison (`analyzed_fingerprint`) and rendered stale-result warning banners across Tabs 1, 2, and 3. Added full buffer clear reset.
- **Verification:** Verified via `tests/test_notice_fingerprint_stale.py`.

### BUG-009: Sidebar Button Styling Collision & Mobile Horizontal Overflow
- **Reproduction:** Generic button CSS centered utility buttons and caused horizontal scrolling on 390px mobile screens.
- **Root Cause:** Unscoped `.stButton > button` CSS rules.
- **Files Changed:** `src/notice2action/ui/styles.py`.
- **Fix Implemented:** Scoped navigation styling to `[class*="st-key-sidebar_nav_"]`, added responsive column wrapping at `<= 768px`, and enforced `overflow-x: hidden !important; max-width: 100vw;`.
- **Verification:** Tested across 6 viewports with Playwright; 0 horizontal overflow.
