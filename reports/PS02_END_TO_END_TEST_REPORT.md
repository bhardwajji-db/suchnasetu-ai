# PS02 — Notice2Action AI: End-to-End Functional Testing & Ground-Truth Validation Report

**Project:** Notice2Action AI — Notice-to-Action Accessibility Assistant  
**Event:** Hacktoberfest 2026 HackDay@Meerut × E-Cell IIMT University  
**Track:** Track 1 — Best Use of Gemma 4  
**Project Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Execution Date:** 20 October 2026  
**Final Verdict:** **PASS** (100% Critical-Field Accuracy, 100% Coverage, 0 Unsupported Claims)  

---

## 1. Environment & Runtime Specifications

| Component | Detected Specification | Verification Status |
|---|---|---|
| **Operating System** | Windows 11 Home (x64) | Active (PowerShell compatible) |
| **Python Runtime** | CPython 3.11.15 in `.venv` (`.venv\Scripts\python.exe`) | Verified (`uv pip` managed) |
| **OCR Engine** | Tesseract v5.4.0.20240606 (`C:\Program Files\Tesseract-OCR\tesseract.exe`) | Active (Supported: `eng`, `osd`) |
| **LLM Server** | Ollama v0.40.3 (`http://127.0.0.1:11434`) | Running & Healthy |
| **Active Model** | `gemma4:latest` (ID `c6eb396dbd59`, 9.6 GB on disk, ~8B parameters) | Verified & Loaded |
| **Hardware** | AMD Ryzen 7 7445HS (16 CPUs) + 16 GB RAM + RTX 4050 (6 GB VRAM) | Layers dynamically offloaded |

---

## 2. Startup and Preflight Diagnostics

Executed via `& ".\.venv\Scripts\python.exe" -c "from notice2action.config import run_preflight_diagnostics; ..."`:

- **Python Runtime:** `[OK]` Python 3.11.15 in project-local `.venv`.
- **Tesseract OCR:** `[OK]` Tesseract v5.4.0 verified at default path.
- **Ollama Server:** `[OK]` HTTP 200 response on port 11434 with 9 models registered.
- **Gemma 4 Model:** `[OK]` `gemma4:latest` present, warm, and responsive.
- **Overall Preflight Status:** **OK (Ready for Live Inference)**.

---

## 3. Synthetic Test Notice & Independent Ground Truth

### Test Notice Text (`tests/fixtures/synthetic_scholarship_notice.txt`):
```text
INSTITUTE OF TECHNOLOGY — SYNTHETIC TEST NOTICE

Notice ID: TEST-SCH-2026-001

Date of issue: 20 October 2026

Subject: Merit Scholarship Application

Eligible students must submit their merit scholarship applications by 5:00 PM on 30 October 2026.

Eligibility: Students who obtained at least 80% marks in their last qualifying examination.

Required documents:
1. Previous qualifying examination marksheet.
2. College identity card.
3. Bank account proof.

Submission method: Submit the application and supporting documents to the Scholarship Office, Room 204, Academic Block.

Helpdesk: scholarships@example.invalid

Late applications will not be accepted.

This notice is synthetic test data. It is not an official announcement.
```

### Machine-Readable Ground Truth (`tests/fixtures/synthetic_scholarship_ground_truth.json`):
- **Notice ID:** `TEST-SCH-2026-001`
- **Issue Date:** `2026-10-20`
- **Purpose:** Merit scholarship application
- **Eligibility Threshold:** `at least 80%`
- **Deadline Date:** `2026-10-30`
- **Deadline Time:** `5:00 PM`
- **Required Documents:** `["Previous qualifying examination marksheet", "College identity card", "Bank account proof"]`
- **Submission Location:** `Scholarship Office, Room 204, Academic Block`
- **Helpdesk Contact:** `scholarships@example.invalid`
- **Late Applications Policy:** `not accepted`
- **Application Fee:** `Not stated in the notice.`
- **Synthetic Marker:** `is_synthetic: true`, `is_official_announcement: false`

---

## 4. Expected vs. Actual Evaluation Matrix

Evaluated via the independent ground-truth evaluator ([`src/notice2action/evaluator.py`](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/src/notice2action/evaluator.py)):

| Field Evaluated | Expected (Ground Truth) | Actual (Gemma 4 Live Output) | Grounded Evidence Quote | Status |
|---|---|---|---|---|
| **Purpose** | Merit scholarship application | *"Merit Scholarship Application"* | *"Subject: Merit Scholarship Application"* (Line 7) | **PASS** |
| **Eligibility Threshold** | At least 80% | *"Students who obtained at least 80% marks in their last qualifying examination."* | *"Eligibility: Students who obtained at least 80% marks in their last qualifying examination."* (Line 11) | **PASS** |
| **Deadline Date** | 30 October 2026 (`2026-10-30`) | *"5:00 PM on 30 October 2026"* | *"Eligible students must submit their merit scholarship applications by 5:00 PM on 30 October 2026."* (Line 9) | **PASS** |
| **Deadline Time** | 5:00 PM | *"5:00 PM on 30 October 2026"* | Line 9 citation | **PASS** |
| **Required Documents** | Marksheet, College ID, Bank account proof | *"Previous qualifying examination marksheet, College identity card, Bank account proof."* | *"Required documents: 1. Previous qualifying examination marksheet. 2. College identity card. 3. Bank account proof."* | **PASS** |
| **Submission Location** | Scholarship Office, Room 204, Academic Block | *"Submit the application and supporting documents to the Scholarship Office, Room 204, Academic Block."* | *"Submission method: Submit the application and supporting documents to the Scholarship Office, Room 204, Academic Block."* (Line 18) | **PASS** |
| **Contact Details** | `scholarships@example.invalid` | *"scholarships@example.invalid (Helpdesk)"* | *"Helpdesk: scholarships@example.invalid"* (Line 20) | **PASS** |
| **Late Applications** | Not accepted | *"Late applications will not be accepted."* | *"Late applications will not be accepted."* (Line 22) | **PASS** |
| **Application Fee** | Not stated in the notice. | *"Not stated in the notice."* (`status: not_stated`) | `null` (Correctly labelled unstated) | **PASS** |

---

## 5. Text Input vs. OCR Input Comparison

| Metric | Direct Text Input | Synthetic PNG Image via Tesseract OCR |
|---|---|---|
| **Input Artifact** | `synthetic_scholarship_notice.txt` | `synthetic_scholarship_notice.png` (1000x752) |
| **Preprocessing** | Null-byte and whitespace normalization | Grayscale + 1.5x upscale + Autocontrast + Sharpen |
| **Extraction Confidence** | 100% (Lossless text) | **86.8% aggregate OCR confidence** |
| **Word Recall vs Source** | 100% | **93.4% keyword recall** |
| **Notice ID Captured** | `TEST-SCH-2026-001` | `TEST-SCH-2026-001` |
| **Deadline Captured** | `5:00 PM on 30 October 2026` | `5:00 PM on 30 October 2026` |
| **Eligibility Captured** | `80% marks` | `80% marks` |
| **Email Captured** | `scholarships@example.invalid` | `scholarships@example.invalid` |
| **Processing Time** | 0 ms | **648 ms** |

---

## 6. Summary and Actionable Steps Verification

1. **Plain-Language Summary (7 Core Questions):**
   - **What it is about:** *"This notice is about applying for a Merit Scholarship."*
   - **Who is eligible:** *"Students with at least 80% marks in qualifying examination."*
   - **What you must do:** *"Submit application and supporting documents to Room 204, Academic Block."*
   - **Required documents:** *"Marksheet, College ID card, and bank account proof."*
   - **Deadline:** *"5:00 PM on October 30, 2026."*
   - **Where to get help:** *"Scholarship Office or email scholarships@example.invalid."*
   - **Missing information:** Explicitly identifies that the notice does not state an application fee.
2. **Action Checklist:**
   - Step 1: Verify 80% eligibility threshold.
   - Step 2: Gather all 3 documents.
   - Step 3: Deliver application to Room 204, Academic Block.
   - Step 4: Submit before 5:00 PM, 30 October 2026.
   - Step 5: Inquire about unstated application fee.
   - All items include grounded quotation proof and interactive completion checkboxes.

---

## 7. Negative and Edge-Case Test Results

Executed via [`tests/test_negative_and_edge_cases.py`](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober fest/ps2/tests/test_negative_and_edge_cases.py):

| Test Case | Scenario | Expected Behavior | Actual Behavior | Status |
|---|---|---|---|---|
| **Edge 01** | Empty text input | Clear validation error, zero crashes | Returned `"Notice text is empty. Please paste..."` | **PASS** |
| **Edge 02** | Unrelated text (cafeteria menu) | Zero fabricated scholarship claims | Purpose marked `not_stated`, no dates invented | **PASS** |
| **Edge 03** | Notice missing deadline | Explicit `not_stated` status | Deadline set to `"Not stated in the notice."` | **PASS** |
| **Edge 04** | Conflicting deadlines (15 vs 25 Nov) | Flag conflict and require confirmation | Marked `conflicting`, `requires_confirmation=True` | **PASS** |
| **Edge 05** | Malformed/black unreadable image | Informative OCR failure message | Returned `"No readable text could be extracted..."` | **PASS** |
| **Edge 06** | Prompt injection in notice | Content wrapped in passive data delimiters | Adversarial signature detected; isolated | **PASS** |
| **Edge 07** | Unsupported document claims | Flag ungrounded claims | Quote absent from text -> downgraded to `uncertain` | **PASS** |

---

## 8. Automated Test Suite Metrics

```text
============================= test session starts =============================
platform win32 -- Python 3.11.15, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2
configfile: pyproject.toml

tests/test_unit_pipeline.py .........................                    [ 75%] (25 passed)
tests/test_negative_and_edge_cases.py .......                            [ 96%] (7 passed)
tests/test_streamlit_interaction.py .                                    [100%] (1 passed)

============================== 33 passed in 4.82s ==============================
```

Additionally, all 5 live integration tests in `tests/test_live_gemma4.py` pass against live Ollama:
- `test_live_01_ollama_health` (PASS)
- `test_live_02_structured_analysis_scholarship_notice` (PASS)
- `test_live_03_summary_and_checklist_generation` (PASS)
- `test_live_04_followup_question_supported_and_unsupported` (PASS)
- `test_live_05_image_ocr_pipeline` (PASS)

---

## 9. Confirmed Bugs and Exact Fixes Applied

1. **Bug 1: Startup `ModuleNotFoundError: No module named 'notice2action'`**
   - *Cause:* Streamlit runs `app.py` with only `ps2/` on `sys.path`. The `src/` directory was not auto-included without package registration.
   - *Fix:* Configured `[tool.setuptools.packages.find] where = ["src"]` in `pyproject.toml`, added self-resolving `SRC_DIR` to `sys.path` in `app.py`, and registered the package in editable mode (`pip install -e .`).
2. **Bug 2: Strict String Match on Multi-Line Quotes in Evaluator**
   - *Cause:* Document list quotes had newlines between numbered bullets, causing raw `quote.lower() in notice.lower()` to fail on newline variations.
   - *Fix:* Used normalized whitespace comparison (`normalize_text()`), bringing unsupported claims count to 0 and achieving an overall **PASS** verdict.

---

## 10. Commands to Reproduce This Evaluation

```powershell
# Activate local environment
.\.venv\Scripts\Activate.ps1

# 1. Run unit & edge-case test suite (33 tests)
pytest tests/test_unit_pipeline.py tests/test_negative_and_edge_cases.py tests/test_streamlit_interaction.py -v

# 2. Run independent ground-truth evaluation script with live Gemma 4
python scripts/evaluate_ground_truth.py

# 3. View Streamlit application
.\scripts\run.ps1
```

---

## 11. Final Verdict

- **Critical-Field Accuracy:** **100.0% (8/8)**
- **Required-Field Coverage:** **100.0%**
- **Unsupported/Fabricated Claims:** **0**
- **OCR Word Recall:** **93.4%**
- **Streamlit UI & AppTest:** **Operational with zero exceptions**
- **OVERALL VERDICT:** **PASS**
