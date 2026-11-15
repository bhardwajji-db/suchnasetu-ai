# SochnaSetu AI — Master Implementation Plan & Execution Blueprint

**Target Codebase:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Evaluation Role:** Senior Software Architect, OCR Research Engineer, AI/ML Engineer, React Engineer & QA Lead  
**Date:** 2026-11-14  
**Status:** Approved for Implementation Planning — Ready for Phased Execution  

---

## 1. Executive Summary & Purpose

This document represents the definitive, approved execution roadmap for elevating **SochnaSetu AI** into a production-grade, highly accurate, and privacy-first civic intelligence assistant, perfectly tailored for submission as a **Computer Organization and Architecture (COA) Laboratory Mini-Project**.

Based on empirical testing across **98 frontend unit tests** and **448 backend integration tests**, this plan resolves critical OCR orientation blindspots, numeral token splits, and hardcoded domain overfitting, while adding an interactive **Human-in-the-Loop OCR correction workbench**, a **split-screen modern document intelligence UI**, and **SIMD hardware benchmark demonstrations**.

---

## 2. Most Critical Problems & Targeted Solutions

```
+---------------------------------------------------------------------------------------------------------------+
| Problem / Defect                   | Severity | Root Cause                     | Engineered Solution          |
+---------------------------------------------------------------------------------------------------------------+
| 1. Tesseract OSD Orientation Fails | P0       | image_to_osd fails on short    | 4-quadrant edge density &     |
|    on notices with <15 text lines  | Critical | notices (<15 lines of text)    | Radon variance fallback pass |
|                                    |          |                                |                              |
| 2. Numeral & Date Spacing Errors   | P1       | Spatial IoU fusion introduces  | Post-processing regex cleanup|
|    (e.g. 15/1 1/2026)              | High     | intra-numeral whitespace       | + relaxed grounding pattern  |
|                                    |          |                                |                              |
| 3. Hardcoded Gazette Overfitting   | P1       | Literal signatory names and    | Decouple into conditional    |
|    embedded in general OCR loop    | High     | numbers hardcoded in ocr.py    | GazettePostProcessor plugin  |
|                                    |          |                                |                              |
| 4. RapidOCR ONNX Adapter Inert     | P1       | Package missing from runtime   | Add rapidocr-onnxruntime and |
|    (falls back to slow Tesseract)  | High     | environment dependencies       | wire token coordinate boxes  |
|                                    |          |                                |                              |
| 5. Missing Token-Level HITL Review | P1       | Citizens cannot edit raw OCR   | Red zigzag underline editor  |
|    prior to factual grounding      | High     | words directly in viewer       | + token re-grounding API     |
+---------------------------------------------------------------------------------------------------------------+
```

---

## 3. Four-Phase Phased Implementation Roadmap

```
Phase 1: Stabilization & OCR Accuracy Hardening (Days 1–3) [Complexity: Moderate]
  ├── TASK-P0-01: Fix Tesseract OSD orientation failure on short notices.
  ├── TASK-P0-02: Add development loopback bypass to CSRF middleware.
  ├── TASK-P1-01: Implement intra-numeral space normalization regex.
  └── TASK-P1-02: Decouple hardcoded Gazette vocabulary into a dedicated plugin.

Phase 2: Human-in-the-Loop Review & Database v6 (Days 4–7) [Complexity: High]
  ├── TASK-P2-01: Execute Database Migration 6 (ocr_tokens, correction_memory, FTS5).
  ├── TASK-P1-03: Activate RapidOCR ONNX adapter with token bounding boxes.
  ├── TASK-P1-04: Implement backend `/api/ocr/correct-token` and re-grounding routes.
  └── TASK-P1-05: Build interactive red zigzag OCR token editor popover in React.

Phase 3: Split-Screen Frontend Redesign & PDF Export (Days 8–10) [Complexity: Moderate]
  ├── TASK-P2-02: Modernize layout into synchronized split-screen workspace.
  ├── TASK-P2-03: Implement server-side binary PDF dossier generation (`/api/export/pdf`).
  ├── TASK-P2-04: Implement frontend view lazy loading (`React.lazy`).
  └── TASK-P3-02: Resolve 18 frontend Oxlint synchronous setState warnings.

Phase 4: Academic COA Defense & Viva Package (Days 11–14) [Complexity: Low-Moderate]
  ├── TASK-P3-01: Build standalone CLI SIMD vs. Scalar hardware benchmark tool.
  ├── Assemble hardware interaction presentation slides (SIMD AVX2, Cache hierarchy, DMA).
  └── Run full regression benchmark gates and compile final mini-project submission.
```

---

## 4. Exact First Implementation Task

> 🎯 **Immediate Starting Task: `[TASK-P0-01] Fix Tesseract OSD Orientation on Short Notices`**
>
> - **File:** `src/notice2action/ocr.py` $\to$ `detect_image_orientation(image: Image.Image)`
> - **Objective:** Resolve the silent failure of `image_to_osd` on single-paragraph notices and posters.
> - **Impact:** Guarantees that sideways scans (90°/270°) automatically rotate upright before reaching the OCR extraction engine, converting previously unreadable documents into 100% extractable circulars.
> - **Safety:** 100% self-contained in `ocr.py`; zero database or frontend dependencies.

---

## 5. Testing & Regression Strategy

To guarantee that no existing features are damaged during execution:
1. **Frontend Gate:** `npm test` (all 26 test files / 98 tests) and `npm run build` must complete with 0 errors before and after any frontend change.
2. **Backend Gate:** `pytest tests/test_gazette_ocr_benchmark.py tests/test_evidence_based_ocr_accuracy.py tests/test_auth.py` must maintain 100% pass rates.
3. **Empirical OCR Benchmark Gate:**
   - `synthetic_scholarship_notice.png`: CER must remain $\le 0.69\%$.
   - `gazette_corrigendum_2017.jpeg`: CER must remain $\le 2.75\%$ (Target: $<1.50\%$).
   - Critical Field Accuracy: Must maintain $\ge 95.2\%$.

---

## 6. Planning Documentation Manifest

All 10 comprehensive planning documents are generated and stored in:  
📁 **`C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2\MASTER_IMPROVEMENT_PLAN/`**

1. [01_CURRENT_STATE.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/01_CURRENT_STATE.md) — Complete baseline analysis, test pass rates, and scorecard.
2. [02_OCR_IMPROVEMENT_PLAN.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/02_OCR_IMPROVEMENT_PLAN.md) — Solutions for OSD orientation, ONNX RapidOCR, numeral spaces, and table extraction.
3. [03_HUMAN_REVIEW_ARCHITECTURE.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/03_HUMAN_REVIEW_ARCHITECTURE.md) — Side-by-side coordinate mapping, red zigzag underlines, and token re-grounding.
4. [04_FRONTEND_REDESIGN_PLAN.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/04_FRONTEND_REDESIGN_PLAN.md) — 12-view redesign specifications, design tokens, and split-screen workspace.
5. [05_NEW_FEATURES_ROADMAP.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/05_NEW_FEATURES_ROADMAP.md) — Feasibility matrix for PDF export, correction memory, FTS5 search, and COA tools.
6. [06_DATABASE_AND_API_CHANGES.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/06_DATABASE_AND_API_CHANGES.md) — SQLite Schema Migration 6 script, new routes, and Pydantic schemas.
7. [07_TESTING_STRATEGY.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/07_TESTING_STRATEGY.md) — Multi-tier test pyramid, ground-truth CER/WER gates, and test commands.
8. [08_IMPLEMENTATION_TASKS.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/08_IMPLEMENTATION_TASKS.md) — 13 detailed work packages ranked by priority (P0 to P3).
9. [09_RISK_AND_DEPENDENCY_ANALYSIS.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/09_RISK_AND_DEPENDENCY_ANALYSIS.md) — Risk mitigation matrix, privacy guarantees, and dependency graph.
10. [MASTER_IMPLEMENTATION_PLAN.md](file:///C:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/MASTER_IMPROVEMENT_PLAN/MASTER_IMPLEMENTATION_PLAN.md) — Grand executive synthesis and phased roadmap.
