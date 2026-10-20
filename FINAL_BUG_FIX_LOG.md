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
- **Fix Implemented:** Killed stale background processes and restarted fresh Streamlit daemon.
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

### BUG-005: Non-Interactive Sidebar Navigation Items
- **Reproduction:** Clicking sidebar navigation items (`📥 1. Process Notice`, `🔍 2. Extracted Facts`, `📋 3. Summary & Actions`, `💬 4. Follow-Up Q&A`) performed zero action.
- **Root Cause:** Sidebar navigation items were rendered as static HTML `<div class="sidebar-nav-item">` strings via `st.markdown()`.
- **Files Changed:** `app.py`, `src/notice2action/ui/styles.py`.
- **Fix Implemented:** Replaced static divs with 4 native `st.button` controls styled dynamically (`type="primary"` when active, `type="secondary"` when inactive), and bound to `st.session_state.active_tab_index` with client-side tab switching.
- **Verification:** `tests/test_ui_controls_comprehensive.py::test_ui_control_01_sidebar_navigation_buttons` passed.

### BUG-006: Gemma 4 JSON Truncation on Large Notices
- **Reproduction:** Analyzing `sample_scholarship_notice.txt` with live Gemma 4 failed with `json.decoder.JSONDecodeError: Expecting ',' delimiter: line 31 column 4 (char 2284)`.
- **Root Cause:** Ollama's `num_predict` was set to `2048` and `num_ctx` to `3072`. Thinking tokens plus output exceeded 2048, cutting off output in the middle of a string.
- **Files Changed:** `src/notice2action/llm/ollama_client.py`.
- **Fix Implemented:** Increased `num_predict` to `4096` and `num_ctx` to `8192`. Added regex trailing comma cleanup in `clean_llm_json_response()`.
- **Verification:** `tests/test_live_gemma4.py::test_live_02` and `test_live_03` passed in live Ollama execution.

### BUG-007: Scanned OCR Demo Images Did Not Display
- **Reproduction:** Loading the scanned notice OCR demo from the sidebar failed to display the image or OCR buttons in Tab 1.
- **Root Cause:** Image rendering and OCR buttons were nested inside `if uploaded_file is not None:`. When loaded from the sidebar sample loader, `uploaded_file` was `None`.
- **Files Changed:** `app.py`.
- **Fix Implemented:** Decoupled image rendering from `file_uploader`. Now displays whenever `st.session_state.uploaded_image is not None`.
- **Verification:** `tests/test_ui_controls_comprehensive.py::test_ui_control_02_synthetic_demo_loaders` passed.

### BUG-008: Suggested Q&A Inquiries Overwritten by Streamlit Lifecycle
- **Reproduction:** Clicking suggested inquiry buttons in Tab 4 did not populate the text input box.
- **Root Cause:** Streamlit widget keys take precedence over `value` parameter across reruns, causing the empty input box to overwrite the suggestion variable.
- **Files Changed:** `app.py`.
- **Fix Implemented:** Directly bound suggested buttons to `st.session_state.qa_input_text_box`. Added a "🗑️ Clear Q&A History" button.
- **Verification:** `tests/test_ui_controls_comprehensive.py::test_ui_control_05_followup_suggested_inquiries` passed.

### BUG-009: Missing Calendar (.ics) Download in Tab 3
- **Reproduction:** Users on Tab 3 (Summary & Action Checklist) could download Markdown but could not download Calendar (.ics) events without navigating to Tab 1.
- **Root Cause:** Tab 3 export block only rendered the Markdown download button.
- **Files Changed:** `app.py`.
- **Fix Implemented:** Added "📅 Add Deadline to Calendar (.ics)" download button in Tab 3 directly alongside Markdown.
- **Verification:** `tests/test_ui_controls_comprehensive.py::test_ui_control_04_ics_and_markdown_exports` passed.
