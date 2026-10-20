# TEST RESULTS MATRIX — NOTICE2ACTION AI (PS02)

| Test Area | Exact Test / Command | Result | Evidence / Notes |
|---|---|---|---|
| **Package Imports** | `python -c "import notice2action; import app"` | **PASS** | Imports cleanly without error; `sys.path` correctly includes `src/`. |
| **Full Pytest Suite** | `pytest tests/ -v -m "not live_llm" --ignore=tests/test_live_gemma4.py --ignore=tests/test_playwright_e2e.py --ignore=tests/test_playwright_workflow.py` | **PASS** | 53 collected, 53 passed, 0 failed, 0 skipped in 15.84s. |
| **Notice Fingerprint & Stale Buffer** | `pytest tests/test_notice_fingerprint_stale.py -v` | **PASS** | 3/3 tests pass (buffer wipe, stale hash warning, empty notice guard). |
| **Comprehensive UI Controls** | `pytest tests/test_ui_controls_comprehensive.py -v` | **PASS** | 8/8 tests pass (sidebar buttons, demo loaders, buffer clear, export, suggested Q&A, jumps, checklist, analyze trigger). |
| **Schema Normalization** | `tests/test_structured_notice_regression.py` | **PASS** | 8/8 tests pass covering strings, dicts, nulls, and malformed inputs. |
| **Negative & Edge Cases** | `tests/test_negative_and_edge_cases.py` | **PASS** | 7/7 edge tests pass (empty text, injection, missing deadline, conflicting). |
| **Streamlit Interaction** | `tests/test_streamlit_interaction.py` | **PASS** | 2/2 AppTest tests pass verifying 4 tabs, widgets, and structured notice render. |
| **Unit Pipeline** | `tests/test_unit_pipeline.py` | **PASS** | 25/25 tests pass covering end-to-end processing without external calls. |
| **Tesseract OCR Recall** | `scripts/evaluate_ground_truth.py` [Step 1] | **PASS** | 86.8% OCR word confidence; 93.4% word recall against synthetic PNG. |
| **Live Gemma 4 Extraction** | `pytest tests/test_live_gemma4.py -v` | **PASS** | 5/5 live tests pass in 153.23s on local GPU; 0 timeouts. |
| **Ground-Truth Evaluation** | `scripts/evaluate_ground_truth.py` [Step 3] | **PASS** | 100.0% Critical Field Accuracy (8/8); 100.0% Coverage; 0 hallucinations. |
| **Playwright Responsiveness** | `pytest tests/test_playwright_e2e.py -v` | **PASS** | 6 viewports tested in real headless Chrome; 0 horizontal overflow. |
| **Playwright E2E Workflow** | `pytest tests/test_playwright_workflow.py -v` | **PASS** | Full live Gemma 4 browser workflow completed in 38.08s; 10 screenshots captured. |
| **HTTP Health Endpoint** | `Invoke-WebRequest http://localhost:8501/_stcore/health` | **PASS** | HTTP 200 OK (`status: ok`). |
| **Release Archive** | `scripts/package_release.ps1` | **PASS** | `release/notice2action_ps02_release.zip` created (clean production archive). |
