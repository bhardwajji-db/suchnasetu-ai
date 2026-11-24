# SochnaSetu AI — Universal Multilingual OCR Implementation & Rollout Roadmap

**Document Version:** 1.0.0  
**Design Date:** November 24, 2026  
**Author:** Principal Software Architect, Release Manager & Engineering Lead  
**Repository Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Execution Status:** PROPOSED ENGINEERING ROADMAP (PENDING USER APPROVAL)  
**Strict Condition:** AUDIT AND DESIGN ONLY — ZERO CODE MODIFICATIONS UNDERTAKEN

---

## 1. Executive Summary

This roadmap outlines the phased, risk-managed engineering schedule for upgrading **SochnaSetu AI** from its current bilingual production baseline (English + Hindi) to comprehensive coverage across **all 22 Indian Scheduled Languages**.

The implementation is structured across **six progressive phases**. Each phase contains strict entry/exit criteria, empirical regression guardrails, and non-breaking backward compatibility rules to ensure the existing production-ready system remains 100% operational throughout the enhancement lifecycle.

---

## 2. Master Implementation Phases Overview

```
[Phase 1: Script Classifier] ──> [Phase 2: Tesseract Assets] ──> [Phase 3: Multi-Script Fusion]
            │                                                                  │
            ▼                                                                  ▼
[Phase 4: IndicOCR Adapter]   ──> [Phase 5: 230-Doc Benchmark] ──> [Phase 6: UI & Fonts]
```

---

## 3. Detailed Phase Breakdown

### Phase 1: Script Detection & Unicode Classifier Expansion
- **Objective:** Expand `src/notice2action/language_detection.py` from 10 constitutional scripts to all 22 scheduled languages.
- **Tasks:**
  1. Add Unicode block regex matchers for Ol Chiki (`\u1C50`–`\u1C7F`), Meetei Mayek (`\uABC0`–`\uABFF`), and Odia (`\u0B00`–`\u0B7F`).
  2. Implement Devanagari regional language disambiguation lexicons for Bodo (`brx`), Dogri (`doi`), Maithili (`mai`), Konkani (`kok`), and Nepali (`nep`).
  3. Add ISO-639 language registry mapping linking detected scripts to corresponding OCR engine identifiers.
- **Verification Gate:** 100% classification accuracy across all 23 language test strings in `tests/fixtures/demo_library/`.

---

### Phase 2: Tesseract Model Asset Provisioning
- **Objective:** Bundle high-quality `tessdata_fast` integerized LSTM models for standard Indic scripts.
- **Tasks:**
  1. Provision 14 official models into `assets/tessdata/`:
     `asm`, `ben`, `guj`, `kan`, `mal`, `mar`, `nep`, `ori`, `pan`, `san`, `snd`, `tam`, `tel`, `urd`.
  2. Update `Dockerfile` Stage 2 to include corresponding `tesseract-ocr-*` system packages for cloud runtime.
  3. Update `get_available_tesseract_languages()` in `src/notice2action/ocr.py` to auto-discover newly mounted models.
- **Verification Gate:** `get_available_tesseract_languages()` returns 17+ languages without warnings.

---

### Phase 3: Generalization of Multi-Script Spatial IoU Token Fusion
- **Objective:** Generalize the proven English date/numeral spatial fusion algorithm across all 22 scripts.
- **Tasks:**
  1. Refactor `_fuse_bilingual_tokens()` in `src/notice2action/ocr.py` from hardcoded Hindi/Devanagari logic into a script-agnostic spatial fusion pipeline.
  2. Maintain parallel primary pass (`lang="<detected_lang>+eng"`) and secondary pass (`lang="eng"`).
  3. Calibrate overlapping bounding boxes (IoU > 0.50) containing Arabic numerals (`0-9`), monetary symbols (`₹`, `Rs.`), and date delimiters (`/`, `-`).
- **Verification Gate:** Category A English CER $\le 3.5\%$; Gazette CER $\le 2.75\%$; regional circular dates transcribed with 100% exact match.

---

### Phase 4: AI4Bharat IndicOCR ONNX Adapter for Specialized Scripts
- **Objective:** Integrate a lightweight, local ONNX adapter for scripts unsupported by standard Tesseract (Santali Ol Chiki, Manipuri Meetei Mayek, and Kashmiri Nastaliq).
- **Tasks:**
  1. Create `src/notice2action/ocr_indic.py` implementing the existing `OCREngine` abstract base class.
  2. Wrap ONNX runtime inference with automatic CPU thread pooling.
  3. Implement automatic dispatch: Route `sat`, `mni`, and `kas` to `IndicOCREngine`; route standard scripts to `TesseractOCREngine`.
- **Verification Gate:** Ol Chiki and Meetei Mayek sample notices transcribing without falling back to English ASCII noise.

---

### Phase 5: Empirical 230-Document Benchmark & Regression Verification
- **Objective:** Execute the standardized evaluation protocol specified in `OCR_BENCHMARK_PLAN.md`.
- **Tasks:**
  1. Ingest 10 documents per language across all 23 target languages (230 total notices).
  2. Record CER, WER, Line match, and Critical Entity Match Rate.
  3. Profile memory footprint (`tracemalloc`) and execution time per page.
  4. Generate automated comparison report `reports/UNIVERSAL_OCR_BENCHMARK_RESULTS.md`.
- **Verification Gate:**
  - Zero regression on Gazette 2017 baseline (CER $\le 2.75\%$).
  - Zero regression on Category E Hindi scans (CER $\le 13.0\%$).
  - Mean CER across all 22 languages $\le 8.5\%$.
  - Peak memory $\le 380\text{MB}$ RAM.

---

### Phase 6: Frontend UI, Font Bundles & Bounding-Box Overlay
- **Objective:** Ensure seamless client-side rendering of all 13 Indian scripts in the React 19 UI.
- **Tasks:**
  1. Update `frontend/src/components/Header.tsx` language dropdown to expose all 22 Scheduled Languages grouped by region.
  2. Bundle open-source Noto Sans font families for Meetei Mayek (`Noto Sans Meetei Mayek`) and Ol Chiki (`Noto Sans Ol Chiki`) into `frontend/src/index.css`.
  3. Verify that `OriginalNoticeViewerModal.tsx` renders bounding boxes with correct coordinate alignment across RTL (Urdu/Kashmiri/Sindhi) and LTR scripts.
- **Verification Gate:** `npm run build` compiles cleanly; Vitest 97/97 tests pass; 0 visual text overflows on mobile viewports.

---

## 4. Strict Safety Rules & Preservation Invariants

1. **Audit & Research Only:** No source code in `src/`, `frontend/`, or `tests/` has been altered during this assessment.
2. **No Model Downloads:** No `.traineddata` or ONNX model files have been downloaded into the workspace without user approval.
3. **Branch Isolation:** `integration-master` and remote Pull Request #1 remain untouched and clean.
4. **Working Tree Cleanliness:** `git status` reflects zero uncommitted source code modifications.

---

## 5. Next Steps & Approval Gateway

This concludes the complete Universal Multilingual OCR Improvement Assessment. 

**Awaiting your explicit instruction:**
Please review the six delivered architecture documents. Once you review and approve the design, we can systematically proceed to Phase 1 of the implementation roadmap.
