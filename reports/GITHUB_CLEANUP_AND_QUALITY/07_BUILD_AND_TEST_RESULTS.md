# 07. BUILD & TEST RESULTS — SOCHNASETU AI

---

## 1. Backend Pytest Regression Results

- **Command:** `.venv\Scripts\python -m pytest tests/`
- **Total Tests Collected:** 213
- **Passed:** **213 (100.0%)**
- **Failed:** **0**
- **Elapsed Duration:** 684.10 seconds (11 minutes 24 seconds)
- **Key Modules Tested:**
  - `tests/test_api_endpoints.py` — 16 passed
  - `tests/test_live_gemma4.py` — 5 live Ollama inference passed
  - `tests/test_hindi_ocr.py` — 6 passed
  - `tests/test_eligibility_engine.py` — 6 passed
  - `tests/test_evidence_trust_engine.py` — 6 passed
  - `tests/test_feature_comprehensive_matrix.py` — 10 passed
  - `tests/test_synthetic_demo_suite.py` — 5 demo notices passed
  - `tests/test_unit_pipeline.py` — 25 core pipeline passed

---

## 2. Frontend Vitest Results

- **Command:** `npm --prefix frontend test -- --run`
- **Total Test Files:** 17 passed (17)
- **Total Tests:** **38 passed (38)**
- **Failed:** **0**
- **Elapsed Duration:** 7.15 seconds
- **Key Suites Tested:**
  - `MultilingualSwitching.test.tsx` (5 passed)
  - `ResponsiveViewportMatrix.test.tsx` (11 passed across 7 viewports)
  - `ActionChecklistTable.test.tsx` (1 passed)
  - `EvidenceInspectorDrawer.test.tsx` (1 passed)
  - `GroundedQAChat.test.tsx` (2 passed)

---

## 3. Frontend Production Build

- **Command:** `npm --prefix frontend run build`
- **TypeScript:** `tsc -b` passed with **0 errors**.
- **Vite:** 1,968 modules transformed; built in **645ms**.
- **Output:**
  - `dist/index.html` (0.73 kB)
  - `dist/assets/index-B_1lZCPV.css` (48.69 kB)
  - `dist/assets/index-B7xew3jC.js` (591.13 kB)
