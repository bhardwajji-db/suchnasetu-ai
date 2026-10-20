# FINAL TEST RESULTS MATRIX — NOTICE2ACTION AI (PS02)

| Test Area | Exact Test / Command | Passed / Failed / Skipped | Actual Output / Evidence | Fix Applied (if applicable) |
|---|---|---|---|---|
| **Python Imports** | `python -c "import notice2action; import app"` | **PASSED** (2/2) | Clean import; `sys.path` initialized. | Package discovery in `pyproject.toml` |
| **Unit Pipeline Suite** | `pytest tests/test_unit_pipeline.py -v` | **PASSED** (25/25) | 25 passed in 4.58s | Preflight checks & mocks isolated |
| **Edge & Negative Suite** | `pytest tests/test_negative_and_edge_cases.py -v` | **PASSED** (7/7) | 7 passed in 1.05s | Boundary & injection checks |
| **Streamlit Interaction** | `pytest tests/test_streamlit_interaction.py -v` | **PASSED** (2/2) | 2 passed in 2.12s | Added `to_ics_bytes()` to schema |
| **Pydantic Regression** | `pytest tests/test_structured_notice_regression.py -v` | **PASSED** (8/8) | 8 passed in 0.26s | Added pre-validators for dicts/nulls |
| **Combined Pytest** | `pytest tests/ -v` | **PASSED** (42/42) | 42 passed in 6.34s | Zero regressions across test suite |
| **Tesseract OCR** | `scripts/evaluate_ground_truth.py` [Step 1] | **PASSED** | 86.8% confidence; 93.4% word recall | Grayscale + adaptive thresholding |
| **Live Gemma 4 Extraction** | `scripts/evaluate_ground_truth.py` [Step 2] | **PASSED** | 30.12s inference; all 8 fields grounded | GPU offload via local Ollama |
| **Ground-Truth Accuracy** | `scripts/evaluate_ground_truth.py` [Step 3] | **PASSED** | 8/8 critical fields correct; 0 hallucinations | Verbatim quotation verification |
| **12-Step User Journey** | `scratch/test_complete_user_journey.py` | **PASSED** (12/12) | 12/12 steps pass end-to-end | Balanced 2-column input workspace |
| **Streamlit Health Check** | `Invoke-WebRequest http://localhost:8501/_stcore/health` | **PASSED** | HTTP 200 OK (`status: ok`) | Fresh daemon process `task-1360` |
| **Release Archive Creation** | `scripts/package_release.ps1` | **PASSED** | 61 clean files, 0.14 MB | Excluded `.venv` and caches |
| **Browser Driver Automation** | Playwright / Selenium Browser Test | **BLOCKED** | ModuleNotFoundError: No module 'playwright' | Documented honestly; tested via AppTest |
