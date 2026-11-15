# ADVERSARIAL OCR & INTELLIGENCE DEFECT REGISTER

**Project:** SochnaSetu AI  
**Repository:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Test Suite:** `tests/adversarial_ocr/`  
**Results Source:** `reports/ADVERSARIAL_OCR_RESULTS.json`  

---

## 1. Executive Defect Summary

During the execution of **550 adversarial OCR and intelligence test cases** across **55 distinct synthetic notices**, a total of **70 defects** were formally recorded.

| Defect Severity | Count | Primary Impact Area |
|---|---|---|
| **CRITICAL** | 3 | Hallucination of eligibility requirement on notices where criteria were completely omitted |
| **HIGH** | 11 | Unnoticed contradictions: Failure of fallback engine to flag conflicting dates, fees, and venues |
| **HIGH** | 55 | OCR failure under non-uniform shadow/lighting gradients (Global thresholding failure) |
| **MEDIUM** | 1 | Cyrillic Unicode homoglyph injection vulnerability in authority entity parsing |
| **Total** | **70** | |

---

## 2. Critical Defects: Hallucination on Missing Data

### DEF-CRIT-01: Hallucination of Boilerplate Eligibility When Omitted
- **Defect ID:** `DEF_HALLUC_INCOMPLETE_B04_MISSING_ELIGIBILITY_clean_eligibility`
- **Severity:** `CRITICAL`
- **Component:** `src/notice2action/analysis.py` (`_deterministic_fallback_extraction`)
- **Test Case:** Notice `B04_MISSING_ELIGIBILITY` (NSDC Skill Grant notice containing no eligibility clause).
- **Expected Behavior:** Notice analyzer must report eligibility as `"Not stated in the notice."` with certainty status `not_stated`.
- **Actual Behavior:** System assigned `"Review criteria and minimum qualifications stated in the notice body."` as an affirmative `stated` fact.
- **Evidence / Output:**
  ```json
  "eligibility": {
    "field_name": "eligibility",
    "value": "Review criteria and minimum qualifications stated in the notice body.",
    "status": "stated",
    "evidence_quote": "Financial support of up to Rs 25,000 is available for certified technical trade trainees."
  }
  ```
- **Root Cause:** In `_deterministic_fallback_extraction`, when regex patterns for specific degrees/percentages fail, a static fallback template assigns speculative boilerplate text instead of strictly returning `"Not stated in the notice."`.
- **Recommended Fix:** Enforce a hard null check: If no specific eligibility substring matches, set `value = "Not stated in the notice."` and `status = CertaintyStatus.NOT_STATED`.

---

### DEF-CRIT-02: False Extrapolation of Unavailable Annexure
- **Defect ID:** `DEF_HALLUC_INCOMPLETE_B06_UNAVAILABLE_ANNEXURE_REFERENCE_clean_eligibility`
- **Severity:** `CRITICAL`
- **Component:** `src/notice2action/analysis.py` (`_deterministic_fallback_extraction`)
- **Test Case:** Notice `B06_UNAVAILABLE_ANNEXURE_REFERENCE` (Heavy Water Board notice citing unattached Annexure-I).
- **Expected Behavior:** System must recognize that Annexure-I is detached and flag eligibility as `"Not stated in the notice."` or `"needs_confirmation"`.
- **Actual Behavior:** The regex parser grabbed the fragment `", age criteria, and pay scales are specified in Annexure-I."` and stored it as a fulfilled factual qualification without flagging the missing reference.
- **Recommended Fix:** Implement reference grounding check: When a field references an external annexure, table, or schedule that is absent from the document body, classify status as `NEEDS_CONFIRMATION` or `UNRESOLVED`.

---

### DEF-CRIT-03: Hallucination of Eligibility on Administrative Tender Notices
- **Defect ID:** `DEF_HALLUC_INCOMPLETE_B08_MISSING_CONTACT_INFO_clean_eligibility`
- **Severity:** `CRITICAL`
- **Component:** `src/notice2action/analysis.py` (`_deterministic_fallback_extraction`)
- **Test Case:** Notice `B08_MISSING_CONTACT_INFO` (Municipal ductile iron pipe supply tender).
- **Expected Behavior:** Tender notices with no applicant qualifications must return `"Not stated in the notice."`.
- **Actual Behavior:** Default regex fallback again injected `"Review criteria and minimum qualifications stated in the notice body."` as a stated fact.
- **Recommended Fix:** Prevent synthetic qualification synthesis on procurement, tender, and civic disruption notices.

---

## 3. High Severity Defects: Unnoticed Contradictions & Conflict Silencing

### DEF-HIGH-01 to DEF-HIGH-11: Failure to Detect Conflicting Notice Instructions
- **Defect IDs:** `DEF_CONTRADICTION_MISSED_C01` through `DEF_CONTRADICTION_MISSED_C11`
- **Severity:** `HIGH`
- **Component:** `src/notice2action/analysis.py` & `src/notice2action/grounding.py`
- **Scope:** All 11 Category C test notices (`C01_CONFLICTING_DEADLINES`, `C02_OFFICIAL_AMENDMENT`, `C03_CONFLICTING_FEES`, `C04_CONFLICTING_REPORTING_TIMES`, `C05_HEADING_BODY_CONTRADICTION`, `C06_CONFLICTING_ELIGIBILITY`, `C07_AMBIGUOUS_DATE_FORMAT`, `C08_CONFLICTING_EXAM_DATES`, `C09_MANUAL_HANDWRITTEN_DATE_OVERRIDE`, `C10_EXPIRED_VS_UPDATED_NOTICE`, `C11_CONFLICTING_VENUE_LOCATION`).
- **Expected Behavior:**
  - Notice `C01`: Flag conflicting application deadlines (15/11/2026 vs 25/11/2026) in `uncertain_or_conflicting_details`.
  - Notice `C02`: Distinguish between superseded original date (20/11/2026) and official corrigendum extension (30/11/2026).
  - Notice `C03`: Flag contradictory fees (Rs 2,000 vs Rs 3,500).
  - Notice `C04`: Flag conflicting reporting times (06:00 AM vs 08:30 AM).
  - Notice `C05`: Flag contradiction between title ("100% Free") and body ("Rs 25,000 non-refundable fee").
- **Actual Behavior:**
  - The deterministic analysis engine captured only the first regex match for each key (`notice_date`, `deadline`, `fee`) and silently discarded subsequent contradictory occurrences.
  - The `uncertain_or_conflicting_details` list remained empty `[]` across all 11 test notices.
- **Evidence / Output:**
  ```json
  "application_deadline": {
    "value": "15/11/2026",
    "status": "stated",
    "evidence_quote": "The portal will strictly close for all submissions on 15/11/2026."
  },
  "uncertain_or_conflicting_details": []
  ```
- **Root Cause:** `_deterministic_fallback_extraction` uses greedy single-match regex patterns (`re.search`) rather than multi-match scanning (`re.finditer`). When multiple conflicting date or currency tokens exist in distinct sections, subsequent matches are completely ignored.
- **Recommended Fix:**
  1. Update regex extraction to find all distinct date, time, and fee tokens across the document.
  2. If multiple distinct non-equivalent values match a field category, populate `uncertain_or_conflicting_details` with evidence quotes for both occurrences.
  3. Mark the primary fact as `status = CertaintyStatus.NEEDS_CONFIRMATION`.

---

## 4. High Severity Defects: Image Degradation Under Shadow Gradients

### DEF-HIGH-12 to DEF-HIGH-66: OCR Collapse Under Non-Uniform Lighting
- **Defect IDs:** `DEF_OCR_A01_shadow` through `DEF_OCR_E11_shadow` (55 test cases)
- **Severity:** `HIGH`
- **Component:** `src/notice2action/ocr.py` (`preprocess_for_tesseract`)
- **Observed Metrics:**
  - Average CER across shadow gradient variations: **76.58%** (Worst case: 94.66% on `E11_HINDI_WEATHER_WARNING`).
  - Average WER across shadow gradient variations: **74.12%**.
  - 50 out of 55 shadow images suffered severe text dropout on the left half of the page.
- **Root Cause Analysis:**
  - `preprocess_for_tesseract()` applies global Otsu thresholding or single-threshold binarization (`cv2.threshold(..., cv2.THRESH_BINARY + cv2.THRESH_OTSU)`).
  - When non-uniform lighting or a shadow gradient is cast across a page (common in smartphone photos of campus notices), the global threshold darkens the shadow region, turning text rows into solid black blocks while washing out bright regions.
- **Recommended Fix:**
  - Replace global thresholding with **Adaptive Gaussian / Sauvola thresholding** (`cv2.adaptiveThreshold(..., cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, blockSize=31, C=11)`).
  - Incorporate background illumination estimation via morphological opening (`cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)`).

---

## 5. Summary Defect Matrix

| Defect ID | Severity | Category | Component | Description |
|---|---|---|---|---|
| `DEF_HALLUC_INCOMPLETE_B04` | CRITICAL | Hallucination | `analysis.py` | Invented boilerplate eligibility on unconditioned notice |
| `DEF_HALLUC_INCOMPLETE_B06` | CRITICAL | Hallucination | `analysis.py` | Accepted missing Annexure reference as stated qualification |
| `DEF_HALLUC_INCOMPLETE_B08` | CRITICAL | Hallucination | `analysis.py` | Injected applicant eligibility into civic procurement tender |
| `DEF_CONTRADICTION_MISSED_C01-C11` | HIGH | Logic Error | `analysis.py` | Single-match regex drops contradictory deadlines & fees |
| `DEF_OCR_SHADOW_01-55` | HIGH | OCR Failure | `ocr.py` | Global Otsu thresholding fails on shadow gradients (CER > 75%) |
| `DEF_HOMOGLYPH_D10` | MEDIUM | Security/Sanitization | `analysis.py` | Cyrillic homoglyph (U+0435) bypasses ASCII authority filter |
