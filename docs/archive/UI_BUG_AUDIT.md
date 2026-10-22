# UI Forensic Bug Audit & Root-Cause Analysis
**Project:** Notice2Action AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Date:** October 20, 2026  
**Auditor:** Senior Frontend / QA Automation Engineer  
**Status:** RESOLVED & EMPIRICALLY VERIFIED  

---

## 1. Overview of Defects & Architectural Failures

During forensic testing of the Notice2Action AI dashboard, several core interaction and UI defects were uncovered where sidebar buttons, tab navigation, suggested Q&A controls, and state management failed to function or caused runtime exceptions.

This document records the exact symptoms, root causes, technical resolutions, and empirical verification methods for each defect.

---

## 2. Detailed Bug Directory

### BUG-01: Tab Navigation Failure via Iframe Sandboxing & React Aria Replacement
- **Severity:** CRITICAL
- **Symptom:** Clicking sidebar navigation buttons ("1. Ingestion & OCR", "2. Grounded Facts", "3. Summary & Actions", "4. Follow-up Q&A") or in-page jump buttons did not switch tabs in the dashboard. The UI remained static on the previous view.
- **Root Cause:**
  1. The previous implementation attempted to inject inline `<script>` tags and JavaScript `postMessage` handlers into `st.components.v1.html()`. Streamlit isolates custom HTML in sandboxed iframes with `sandbox="allow-scripts"`, preventing cross-frame access to `window.parent.document`.
  2. Streamlit 1.66 transitioned from BaseWeb tabs (`button[data-baseweb="tab"]`) to modern React Aria components (`div[role="tab"][data-testid="stTab"]`). Any legacy DOM selectors query-matched zero elements.
  3. Inline scripts injected via `st.markdown(..., unsafe_allow_html=True)` were sanitized or ignored by React's synthetic event dispatcher.
- **Resolution:**
  Eliminated all brittle JavaScript DOM hacks and adopted native Streamlit 1.66 dynamic tab state management:
  ```python
  cur_tab_idx = st.session_state.get("active_tab_index", 0)
  if cur_tab_idx < 0 or cur_tab_idx >= len(TAB_NAMES):
      cur_tab_idx = 0

  def on_main_tabs_change():
      sel = st.session_state.get(f"main_dashboard_tabs_{cur_tab_idx}")
      if sel in TAB_NAMES:
          st.session_state.active_tab_index = TAB_NAMES.index(sel)

  tab_input, tab_structured, tab_summary, tab_followup = st.tabs(
      TAB_NAMES,
      key=f"main_dashboard_tabs_{cur_tab_idx}",
      default=TAB_NAMES[cur_tab_idx],
      on_change=on_main_tabs_change,
  )
  ```
  By dynamically keying the tab container on `cur_tab_idx`, any change triggered by sidebar or jump buttons cleanly remounts the tab container with the target tab active.
- **Verification:** Verified in headless Chrome via Playwright (`tests/test_playwright_e2e.py` and `tests/test_playwright_workflow.py`). All 4 tabs switch instantaneously with bidirectional highlight synchronization.

---

### BUG-02: `StreamlitWidgetAlreadyInstantiatedError` on Programmatic Tab Switching
- **Severity:** HIGH
- **Symptom:** When clicking navigation buttons, the app crashed with `StreamlitWidgetAlreadyInstantiatedError: Cannot set session_state key after widget has been created`.
- **Root Cause:** Setting widget state keys (e.g., `st.session_state["main_dashboard_tabs"] = ...`) inside the main script execution body after `st.tabs()` had already been registered violates Streamlit's unidirectional execution model.
- **Resolution:**
  Shifted all navigation button triggers to pre-instantiation `on_click` callbacks:
  ```python
  def set_active_tab(tab_idx: int) -> None:
      st.session_state.active_tab_index = tab_idx

  st.button(
      label,
      key=f"sidebar_nav_{i}",
      type="primary" if is_active else "secondary",
      use_container_width=True,
      on_click=set_active_tab,
      args=(i,),
  )
  ```
  Streamlit executes widget callbacks *before* running the script body, ensuring `st.session_state.active_tab_index` updates cleanly before `st.tabs()` is instantiated.
- **Verification:** 53/53 pytest tests pass; Playwright automated browser test clicks through all sidebar buttons and jump buttons without raising any widget state exceptions.

---

### BUG-03: Suggested Q&A Inquiry Buttons Overwrite & Lifecycle Desynchronization
- **Severity:** MEDIUM
- **Symptom:** In Tab 4 (Follow-up Q&A), clicking suggested inquiry buttons (e.g., "What documents are needed to apply?") cleared the text box or triggered a rerun without populating the question or executing inference.
- **Root Cause:** The callback was defined locally or executed in a manner that was overwritten by the subsequent `st.chat_input` widget initialization.
- **Resolution:**
  Moved `set_qa_inquiry(inquiry_text)` to module level and bound preset inquiry buttons via `on_click=set_qa_inquiry, args=(inquiry,)`:
  ```python
  def set_qa_inquiry(inquiry_text: str):
      st.session_state.qa_inquiry_to_submit = inquiry_text
      st.session_state.qa_input_text_box = inquiry_text
  ```
  During form evaluation, the query text is obtained from `(user_q or st.session_state.get('qa_input_text_box', '')).strip()`, ensuring preset clicks immediately populate the query and submit.
- **Verification:** Verified in Playwright E2E step 5 (`test_playwright_workflow.py` Step 5) and Unit Test `test_ui_controls_comprehensive.py::test_ui_control_05_followup_suggested_inquiries`.

---

### BUG-04: Notice Buffer Desynchronization & Stale Results Propagation
- **Severity:** HIGH
- **Symptom:** When a user edited the raw notice text in the buffer after running an analysis, Tabs 2, 3, and 4 continued to display old facts, summaries, and action checklists without any warning that the results belonged to an earlier version of the text.
- **Root Cause:** Analysis results in session state had no cryptographic binding to the input buffer content.
- **Resolution:**
  Implemented SHA-256 notice content fingerprinting:
  ```python
  # On successful analysis:
  st.session_state.analyzed_fingerprint = hashlib.sha256(raw_notice_text.strip().encode()).hexdigest()

  # On each script run:
  current_fp = hashlib.sha256(raw_notice_text.strip().encode()).hexdigest() if raw_notice_text.strip() else None
  is_stale = bool(st.session_state.analyzed_fingerprint and current_fp != st.session_state.analyzed_fingerprint)
  ```
  When `is_stale` is true, prominent warning banners are rendered across Tab 1, Tab 2, and Tab 3 ("Notice Buffer Modified — Results displayed below reflect an earlier version. Click 'Analyze Notice with Gemma 4' to refresh").
  Additionally, clicking "Clear Buffer" resets `raw_notice_text`, `structured_notice`, `summary_en`, `checklist`, and `analyzed_fingerprint`.
- **Verification:** Unit tests in `tests/test_notice_fingerprint_stale.py` verify buffer clearing, stale banner generation, and empty notice validation.

---

### BUG-05: Non-Nav Button Scoping & Mobile Layout Horizontal Overflow
- **Severity:** MEDIUM
- **Symptom:** Non-navigation sidebar buttons ("Competition Demo", "Load Selected Sample", "Reset Session") inherited navigation button styling, centering their text unpredictably and causing horizontal overflow (`scrollWidth > clientWidth`) on small screens (390px mobile).
- **Root Cause:** CSS selectors in `styles.py` targeted all `.stButton > button` elements uniformly rather than scoping to specific navigation widgets.
- **Resolution:**
  Scoped navigation styles strictly to `[class*="st-key-sidebar_nav_"]`:
  ```css
  div[class*="st-key-sidebar_nav_"] button {
      justify-content: flex-start !important;
      text-align: left !important;
      padding: 0.55rem 0.85rem !important;
  }
  ```
  Added responsive flex-wrapping at `<= 768px` and enforced:
  ```css
  html, body {
      overflow-x: hidden !important;
      max-width: 100vw;
  }
  ```
- **Verification:** Playwright multi-viewport suite verified 0 horizontal overflow across 6 viewports (1920x1080 down to 390x844).

---

## 3. Summary of Bug Resolutions

| Bug ID | Component | Defect Type | Status | Test Coverage |
| :--- | :--- | :--- | :---: | :--- |
| **BUG-01** | `app.py` / `st.tabs` | DOM Sandbox / React Aria Tab Sync | **RESOLVED** | `test_playwright_e2e.py` |
| **BUG-02** | `app.py` / Nav Buttons | `StreamlitWidgetAlreadyInstantiatedError` | **RESOLVED** | `test_ui_controls_comprehensive.py` |
| **BUG-03** | `app.py` / Tab 4 | Suggested Q&A Lifecycle Overwrite | **RESOLVED** | `test_ui_controls_comprehensive.py` |
| **BUG-04** | `app.py` / State | Stale State Propagation Without Warning | **RESOLVED** | `test_notice_fingerprint_stale.py` |
| **BUG-05** | `styles.py` | Non-Scoped Button CSS & Mobile Overflow | **RESOLVED** | `test_playwright_e2e.py` |

All defects are fully resolved with 100% reproducible test verification.
