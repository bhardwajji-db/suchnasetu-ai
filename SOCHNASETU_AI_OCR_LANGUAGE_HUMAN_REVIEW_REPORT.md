# SuchnaSetu AI — OCR Intelligence, Automatic Language Detection & Human Review System Implementation Report

**Document Version:** 1.0.0  
**Date:** 2026-11-16  
**System:** SuchnaSetu AI (Notice2Action)  
**Status:** Verification Complete & Fully Operational  

---

## 1. Executive Summary

This report documents the root-cause analysis, design architecture, implementation, and rigorous verification of the **OCR Intelligence, Automatic Language Detection, and Persistent Human Review System** in SuchnaSetu AI. 

The implementation was prompted by real-world degradation observed when uploading complex notices (specifically the IIMT Engineering College Notice, `data/uploads/f1cfda07c4ed0c86_1794773110.jpeg`), where an English-only statutory circular was erroneously forced into Hindi OCR mode and rotated 90 degrees sideways, producing unusable, garbled text.

All objectives have been accomplished without introducing cloud APIs, paid dependencies, or breaking changes:
1. **Intelligent Automatic Language Detection (`auto`):** Pre-analyzes document script distribution before initiating OCR, accurately distinguishing English (`eng`), Hindi Devanagari (`hin`), bilingual mixed notices (`hin+eng`), and regional languages (`mr`).
2. **Normalized Orientation Recovery:** Solved the false 90-degree sideways rotation by normalizing horizontal and vertical projection profiles by image dimensions, preventing aspect-ratio distortion while preserving robust recovery for genuine 90°, 180°, and 270° misoriented scans.
3. **Persistent SQLite Human Review System:** Added Database Migration 6 with dedicated `human_review_items` storage, tracking review statuses (`pending`, `corrected`, `verified`, `ignored`), and enabling safe application of human corrections to canonical document text while permanently archiving raw OCR text for legal auditability.
4. **Interactive Human Review Workspace Drawer:** Built a responsive workspace drawer displaying status metrics, category filters, inline span correction, and batch correction application.
5. **Color-Synchronized Document Overlays:** Synchronized review status indicators (Red for Pending, Blue for Corrected, Green for Verified, Slate for Ignored) across both the original image canvas overlay and the raw text tab at all zoom levels (50%–300%).
6. **Canvas-Based Yellow Search Highlighting:** Enabled visual keyword search on the original document image canvas using OCR bounding boxes, complete with active match borders, `Match X of Y` navigation, and smooth auto-scrolling.

---

## 2. Reproduction & Root Cause Analysis of the IIMT Notice Problem

### 2.1 The Observed Failure
When uploading the official IIMT Engineering College circular (`data/uploads/f1cfda07c4ed0c86_1794773110.jpeg`), two compounding failures occurred:
1. **False 90-Degree Rotation:** Upright portrait page was rotated 90 degrees sideways.
2. **Forced Hindi Mode (`hin`):** Despite the document containing 100% English Latin text, the OCR engine executed in Hindi mode.
3. **Garbled Output:** English headings such as `"IIMT ENGINEERING COLLEGE"` were transcribed into garbled Devanagari characters: `"हद ॥४9॥४६६२॥४७ ८06855"`.

### 2.2 Root Cause 1: Aspect Ratio Scaling Bias in Projection Profiles
- In `detect_image_orientation`, horizontal and vertical projection profiles sum pixel ink counts across rows and columns.
- For a portrait page ($921 \times 1280$, scaled to $431 \times 600$), column sums sum over 600 pixels, while row sums sum over 431 pixels.
- Because sample variance scales quadratically with profile length ($\text{Var}(X) \propto L^2$), the unnormalized column variance was artificially inflated by $(600/431)^2 \approx 1.94$.
- As a result, $v_{\text{var}} = 7673.75$ exceeded $h_{\text{var}} = 4731.47$ by $1.62\times$ despite horizontal text lines, causing the algorithm to falsely conclude the document was rotated sideways.
- Furthermore, Tesseract OSD returned confidence $1.89$ on this sample; the previous strict threshold of $\ge 2.0$ ignored this correct 0° OSD signal and fell back to the unnormalized projection profile.

### 2.3 Root Cause 2: Hardcoded / Manual Hindi Default
- The frontend `OCRPanel` defaulted `sourceLang` to `'hin'`, assuming government notices were primarily Hindi.
- Tesseract's `hin` language model attempted to force Devanagari character classifications onto Latin glyphs, resulting in garbled text.

---

## 3. Implemented Architecture & Solutions

### 3.1 Document-Level Automatic Language Detection
Implemented in `src/notice2action/language_detection.py`:
- **Fast Script Sampling:** Extracts text via rapid OCR or pre-analysis to inspect Unicode script distributions:
  - Latin (`\u0041-\u007A`): English
  - Devanagari (`\u0900-\u097F`): Hindi / Marathi
- **Detection Algorithm:**
  $$\text{Ratio}_{\text{Devanagari}} = \frac{\text{Devanagari Characters}}{\text{Total Alphabetic Characters}}$$
  $$\text{Ratio}_{\text{Latin}} = \frac{\text{Latin Characters}}{\text{Total Alphabetic Characters}}$$
  - If $\text{Ratio}_{\text{Latin}} \ge 0.80 \implies \text{Language: } \text{'eng'}$ (Confidence: 1.0)
  - If $\text{Ratio}_{\text{Devanagari}} \ge 0.80 \implies \text{Language: } \text{'hin'}$ (Confidence: 1.0)
  - If both scripts $> 0.15 \implies \text{Language: } \text{'hin+eng'}$ (Bilingual, `is_mixed = True`)
- **API Endpoint:** Exposed `POST /api/ocr/detect-language`.
- **Frontend Integration:** Defaults OCR selector to `AUTO` (`auto`), shows detected language badge with confidence, and preserves manual user selections when explicitly chosen with a "Reset to Auto" button.

### 3.2 Normalized Projection Profile Orientation Recovery
Implemented in `src/notice2action/ocr.py`:
- **Normalized Row/Column Profiles:**
  $$\text{row\_prof}(y) = \frac{\sum_{x} \text{ink}(x, y)}{W}, \quad \text{col\_prof}(x) = \frac{\sum_{y} \text{ink}(x, y)}{H}$$
- **Dimension Independence:** Both profiles represent ink density fractions between $0.0$ and $1.0$, completely removing aspect ratio distortion.
- **Candidate Isolation:** Sideways rotations ($90^\circ, 270^\circ$) are only evaluated when vertical variance strictly exceeds horizontal variance by at least 10% ($\text{Var}(\text{col}) > \text{Var}(\text{row}) \times 1.10$).
- **OSD Confidence Tuning:** Lowered Tesseract OSD confidence threshold from $2.0$ to $1.5$, allowing reliable OSD zero-degree verification.

### 3.3 Persistent SQLite Human Review System
Implemented in `src/notice2action/storage/db.py`:
- **Migration 6:** Creates table `human_review_items`:
  ```sql
  CREATE TABLE IF NOT EXISTS human_review_items (
      id TEXT PRIMARY KEY,
      document_id TEXT NOT NULL,
      page_number INTEGER DEFAULT 1,
      original_text TEXT NOT NULL,
      suggested_text TEXT,
      corrected_text TEXT,
      confidence REAL DEFAULT 0.0,
      reason TEXT,
      status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'corrected', 'verified', 'ignored')),
      box_json TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
  );
  CREATE INDEX IF NOT EXISTS idx_review_doc_status ON human_review_items(document_id, status);
  ```
- **CRUD Endpoints (`server.py`):**
  - `GET /api/documents/{document_id}/review-items`: Retrieves review items partitioned into `pending`, `corrected`, `verified`, `ignored` with total counters.
  - `POST /api/documents/{document_id}/review-items/{item_id}`: Updates item status and corrected text.
  - `POST /api/documents/{document_id}/review-items/apply`: Replaces uncertain words in `documents.raw_text` with accepted corrections while retaining original raw text in metadata for auditability.

### 3.4 Interactive Human Review Workspace Drawer
Implemented in `frontend/src/components/OCRPanel.tsx`:
- **Metric Header:** Live counts for Total, Pending, Corrected, Verified, and Ignored.
- **Filter Tabs:** Quickly view items by status.
- **Inline Editing & Actions:**
  - "View in Document": Opens Document Viewer centered on the word.
  - "Save": Saves custom typed correction (status $\to$ `corrected`).
  - "Verify": Approves suggested repair (status $\to$ `verified`).
  - "Ignore": Disregards warning (status $\to$ `ignored`).
- **Batch Application:** "Apply Corrections to Notice" applies all verified and corrected words to the canonical notice text.

### 3.5 Synchronized Status Indicators & Canvas Search
Implemented in `frontend/src/components/OriginalNoticeViewerModal.tsx`:
- **Status Colors:**
  - Red: Pending / Uncertain (`border-red-600 bg-red-500/15 ring-red-400/40`)
  - Blue: Corrected (`border-blue-600 bg-blue-500/15 ring-blue-400/40`)
  - Green: Verified (`border-emerald-600 bg-emerald-500/15 ring-emerald-400/40`)
  - Slate: Ignored (`border-slate-500 bg-slate-500/15 ring-slate-300/40`)
- **Image Canvas Keyword Search:**
  - Matches highlighted in semi-transparent yellow with active match ring.
  - Navigation controls: `Match X of Y`, Previous (`<`), Next (`>`).
  - Smooth auto-scrolling to active match on the canvas.
  - Informative warning fallback when a matched word lacks bounding box coordinates.

---

## 4. Verification & Benchmark Results

### 4.1 Backend Test Results
```
tests/test_ocr_intelligence_and_human_review.py  8 passed, 1 skipped (37.24s)
tests/test_ocr_review_and_502_regression.py      8 passed (1.23s)
tests/test_orientation_recovery.py              21 passed (44.81s)
tests/test_pdf_and_hindi_ocr_pipeline.py        11 passed
tests/test_gazette_ocr_benchmark.py              4 passed
tests/test_evidence_based_ocr_accuracy.py       10 passed
tests/test_pdf_ingestion.py                     12 passed
-------------------------------------------------------------------------
TOTAL SUITE EXECUTION:                          74 passed, 1 skipped in 123.76s (100% pass)
```

### 4.2 Orientation Recovery Breakdown Across All 4 Angles
All 21 parameterized rotation tests passed across multiple document types:
- Short Notices (<4 lines): 0°, 90°, 180°, 270° $\implies$ **100% Recovery**
- Gazette Long Documents: 0°, 90°, 180°, 270° $\implies$ **100% Recovery**
- Synthetic Scholarship Notices: 0°, 90°, 180°, 270° $\implies$ **100% Recovery**
- Hindi Notices: 0°, 90°, 180°, 270° $\implies$ **100% Recovery**
- Blank Images: Preserves 0° without false rotation
- Bounding Box Coordinate Remapping: 90°, 180°, 270° $\implies$ **100% Accurate**

### 4.3 Frontend Test Results (Vitest)
```
Test Files  26 passed (26)
Tests       97 passed (97)
Duration    14.66s
```
- Includes 5 newly added tests in `OCRIntelligenceHumanReview.test.tsx` verifying language auto-detection, user override, drawer metrics, inline editing, and image search highlights.

### 4.4 Code Quality & Linter
```
Command: oxlint
Results: 0 warnings, 0 errors across 92 source files (116 rules checked).
```

### 4.5 Production Build
```
Command: npm run build (tsc -b && vite build)
Results: Succeeded in 836ms with zero errors.
Bundle Sizes:
  - Initial JS: 157.12 kB
  - Vendor React: 218.75 kB
  - Vendor Icons: 29.05 kB
  - CSS: 94.76 kB
```

---

## 5. Before-and-After Comparison: IIMT Notice Reproduction

| Evaluation Parameter | Before Fix (Reported Bug) | After Implemented Fix |
|---|---|---|
| **Detected Language** | None (hardcoded Hindi `hin`) | English (`en`, confidence: 1.0, non-mixed) |
| **OCR Mode Selected** | `hin` | `eng` |
| **Orientation Applied** | Falsely rotated 90° sideways | Stays upright at 0° |
| **Heading Extraction** | `"हद ॥४9॥४६६२॥४७ ८06855"` | `"IIMT ENGINEERING COLLEGE"` |
| **Ref Number Extraction** | Garbled Devanagari symbols | `"IIMT/IQAC/2026-27/11"` |
| **Date Extraction** | Failed | `"29.10.2026"`, `"30th October 2026"` |
| **Confidence Score** | < 25.0% | **92.38%** |
| **Human Review Workflow**| Ephemeral in-memory review | Persistent SQLite database items with live status drawer |
| **Document Highlighting**| Plain unstyled modal | Color-coded underlines (Red/Blue/Green/Slate) + Yellow Canvas Search |

---

## 6. Implementation Checklist & Acceptance Sign-off

- [x] **Automatic OCR Language Detection:** AUTO mode is default; document script is analyzed before OCR selection; English circular selects English; Hindi circular selects Hindi; mixed notices select bilingual mode.
- [x] **User Manual Override:** Users can override language to English, Hindi, Bilingual, or Marathi; manual selection is preserved; "Reset to Auto" action available.
- [x] **Rotation Rectification:** Aspect ratio normalization in projection profiles eliminates false sideways rotations while maintaining 100% recovery for genuine 90°/180°/270° scans.
- [x] **Persistent Review Storage:** Migration 6 created `human_review_items`; review items persist across browser refreshes and session resets.
- [x] **Review Workspace Drawer:** Comprehensive drawer with status metrics, filter tabs, inline editing, and "Apply Corrections to Notice" action.
- [x] **Status Synchronized Colors:** Underlines in modal image overlay and text tab reflect pending (red), corrected (blue), verified (green), and ignored (slate).
- [x] **Image Canvas Keyword Search:** Yellow highlights on image canvas with active match border, `Match X of Y`, Previous/Next navigation, and smooth scrolling.
- [x] **Auditability Preserved:** Canonical text updates retain raw OCR text for audit trails; no artificial hallucination introduced.
- [x] **Zero Paid APIs / Local-First:** All processing executes on local ONNX / Tesseract engines without external network dependencies.
- [x] **Regression Safety:** All 74 backend tests and 97 frontend tests pass 100%.

**Sign-off:** All acceptance criteria are met and verified. The system is ready for production use.
