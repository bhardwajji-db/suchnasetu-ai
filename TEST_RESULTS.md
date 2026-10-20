# TEST RESULTS MATRIX — NOTICE2ACTION AI (PS02)

| Test Area | Exact Test / Command | Result | Evidence / Notes |
|---|---|---|---|
| **Package Imports** | `python -c "import notice2action; import app"` | **PASS** | Imports cleanly without error; `sys.path` correctly includes `src/`. |
| **Full Pytest Suite** | `pytest tests/test_unit_pipeline.py tests/test_negative_and_edge_cases.py tests/test_streamlit_interaction.py tests/test_structured_notice_regression.py -v` | **PASS** | 42 collected, 42 passed, 0 failed, 0 skipped in 6.34s. |
| **Schema Normalization** | `tests/test_structured_notice_regression.py` | **PASS** | 8/8 tests pass covering strings, dicts, nulls, and malformed inputs. |
| **Negative & Edge Cases** | `tests/test_negative_and_edge_cases.py` | **PASS** | 7/7 edge tests pass (empty text, injection, missing deadline, conflicting). |
| **Streamlit Interaction** | `tests/test_streamlit_interaction.py` | **PASS** | 2/2 AppTest tests pass verifying 4 tabs, widgets, and structured notice render. |
| **Tesseract OCR Recall** | `scripts/evaluate_ground_truth.py` [Step 1] | **PASS** | 86.8% OCR word confidence; 93.4% word recall against synthetic PNG. |
| **Live Gemma 4 Extraction** | `scripts/evaluate_ground_truth.py` [Step 2] | **PASS** | 29.65s–34.68s inference time on RTX 4050 GPU; 0 timeouts. |
| **Ground-Truth Evaluation** | `scripts/evaluate_ground_truth.py` [Step 3] | **PASS** | 100.0% Critical Field Accuracy (8/8); 100.0% Coverage; 0 hallucinations. |
| **12-Step User Journey** | `scratch/test_complete_user_journey.py` | **PASS** | 12/12 steps pass in sequence (demo load, analyze, facts, Q&A, Hindi, OCR). |
| **HTTP Health Endpoint** | `Invoke-WebRequest http://localhost:8501/_stcore/health` | **PASS** | HTTP 200 OK (`status: ok`). |
| **Release Archive** | `scripts/package_release.ps1` | **PASS** | `release/notice2action_ps02_release.zip` created (0.14 MB, 61 clean files). |
| **Browser Automation** | Real Browser Driver (Playwright) | **BLOCKED** | Playwright not installed in `.venv`. Verified via AppTest & HTTP probe. |
