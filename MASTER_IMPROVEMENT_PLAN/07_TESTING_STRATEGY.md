# SochnaSetu AI — Comprehensive Testing & Quality Assurance Strategy

**Target Repositories:** `tests/`, `frontend/src/test/`  
**Role:** Senior Quality Assurance & Test Automation Lead  

---

## 1. Testing Philosophy & Non-Regression Principles

SochnaSetu AI serves official civic documentation where errors have direct human consequences. Our testing strategy enforces:
1. **Zero Regression Tolerance:** All **98 existing frontend tests** and **448 existing backend tests** must continue to pass with zero regressions after any code modification.
2. **Deterministic Evaluation:** Grounding, omission checks, and uncertainty classifications must be tested using offline deterministic test adapters, eliminating non-deterministic LLM variance during automated test passes.
3. **Empirical OCR Measurement:** No OCR changes may be claimed as "improvements" without calculating exact Character Error Rate (**CER**) and Word Error Rate (**WER**) against reference ground-truth files in `tests/fixtures/`.

---

## 2. Test Suite Architecture

```
Testing Pyramid
├── Level 1: Unit Test Layer (Sub-Second Execution)
│    ├── Frontend: Vitest + Testing Library (26 files, 98 tests)
│    └── Backend: Pytest Unit Suites (Pydantic validation, regex, token cleanup)
├── Level 2: Component & Integration Layer (1 - 5 Seconds)
│    ├── API Endpoints: FastAPI TestClient with Origin header injection
│    ├── Database Persistence: SQLite WAL transactions across restarts
│    └── Fused OCR: Spatial IoU alignment and token coordinate generation
├── Level 3: Ground-Truth Empirical Benchmarks (5 - 25 Seconds)
│    ├── English Baseline: `synthetic_scholarship_notice.png` (Target CER < 0.5%)
│    └── Mixed Hindi-English Gazette: `gazette_corrigendum_2017.jpeg` (Target CER < 1.5%)
└── Level 4: End-to-End Civic Workflows (Playwright & Mobile Viewports)
     ├── Ingestion -> Standalone OCR -> Review Underlines -> Save Correction
     └── Re-ground Facts -> Verify Canonical 6 Fields -> Export PDF Dossier
```

---

## 3. New Automated Test Suites to Implement

### 3.1 New Frontend Test Suites (`frontend/src/test/`)

| Test Suite File | Primary Objective | Verification Criteria |
|---|---|---|
| `OCRTokenEditorModal.test.tsx` | Tests interactive token correction popover | Renders original OCR text, confidence chip, accepts corrections, cancels cleanly |
| `SplitScreenWorkspace.test.tsx`| Tests synchronized side-by-side layout | Clicking Fact Card scrolls scan to bounding box; zoom persists; red wavy underline renders |
| `CorrectionMemory.test.tsx` | Tests persistent correction suggestions | Repeated misread strings auto-populate with user's past approved replacements |

### 3.2 New Backend Test Suites (`tests/`)

| Test Suite File | Primary Objective | Verification Criteria |
|---|---|---|
| `test_orientation_recovery.py` | Tests 4-quadrant edge density fallback | Recovers 90°, 180°, and 270° rotated synthetic notices with $<15$ text lines |
| `test_numeral_space_repair.py` | Tests regex normalization on split numbers | `15/1 1/2026` -> `15/11/2026`; `Rs. 5 0 0` -> `Rs. 500` without corrupting text |
| `test_hitl_correction_pipeline.py`| Tests `/api/ocr/correct-token` & re-ground | Token edit updates `documents`, resolves uncertainty, re-generates summaries |
| `test_hardware_simd_benchmark.py` | Tests COA SIMD benchmark CLI | Validates AVX2 detection, scalar vs vector execution, confirms $>4x$ speedup |

---

## 4. Ground-Truth Benchmarking Protocol

All OCR modifications must be verified using the standard Levenshtein calculation:
$$\text{CER} = \frac{S + D + I}{N_{\text{ref}}} \times 100\%$$
where $S$ = Substitutions, $D$ = Deletions, $I$ = Insertions, and $N_{\text{ref}}$ = Total characters in ground-truth reference text.

### Mandatory Benchmark Gates Before Merge:
- [ ] `synthetic_scholarship_notice.png`: CER must not exceed **0.69%**.
- [ ] `gazette_corrigendum_2017.jpeg`: CER must not exceed **2.75%** (target: $<1.50\%$).
- [ ] Field Accuracy Score on Gazette critical fields: Must remain $\ge 95.2\%$ (20/21 fields correct).
- [ ] Execution Latency per page: Must not exceed 2.5s for English and 6.5s for dual-pass Devanagari.

---

## 5. Standard Test Execution Commands

```bash
# 1. Run Complete Frontend Test Suite
cd frontend
npm test

# 2. Run Frontend Production Type-Check & Build
npm run build

# 3. Run Frontend Linter
npm run lint

# 4. Run Core Backend Unit & OCR Benchmarks
cd ..
.\.venv\Scripts\Activate.ps1
pytest tests/test_gazette_ocr_benchmark.py tests/test_evidence_based_ocr_accuracy.py -v

# 5. Run Authentication & Security Suites
pytest tests/test_auth.py tests/test_auth_and_real_db_persistence.py tests/test_backend_persisted_auth.py -v

# 6. Run Complete Non-Playwright Backend Suite
pytest tests/ -k "not playwright and not lan" -q
```
