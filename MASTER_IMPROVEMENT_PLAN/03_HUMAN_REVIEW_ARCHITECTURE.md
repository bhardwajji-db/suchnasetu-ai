# SochnaSetu AI — Human-in-the-Loop OCR Review Architecture

**Target Components:** `frontend/src/components/`, `src/notice2action/api/server.py`, `src/notice2action/storage/db.py`  
**Role:** Senior Full-Stack Architect & UX Engineer  

---

## 1. Architectural Vision

While automated OCR and LLM grounding catch over 95% of factual data, official administrative notices require **zero-error tolerance**. An overlooked digit in an application deadline ($15/11$ vs $18/11$) or an altered bank account IFSC code can disenfranchise a citizen.

The **Human-in-the-Loop (HITL) OCR Review Architecture** provides a side-by-side verification workbench where low-confidence words are visually flagged with red zigzag underlines, mapped to their exact pixel coordinates on the original scan, and editable with one click. Corrections immediately re-trigger factual grounding across dependent summaries and citizen action checklists.

---

## 2. End-to-End Human Review Dataflow

```
[ Ingested Document & Scan ]
            │
            ▼
[ OCR Extraction with Token Coordinates ]
  • Each word has: text, conf (0–100), box: [x1, y1, x2, y2], line, page
  • Words with conf < 65 or regex anomaly tagged `is_uncertain = True`
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                 INTERACTIVE SIDE-BY-SIDE SPLIT WORKSPACE                    │
│                                                                             │
│   LEFT PANE: Original Document Image      RIGHT PANE: Synchronized OCR Text │
│  ┌───────────────────────────────────┐   ┌───────────────────────────────┐ │
│  │                                   │   │ Line 14:                      │ │
│  │   Scholarship applications must   │   │ Scholarship applications must │ │
│  │   be submitted by [15/11/2026]    │   │ be submitted by [15/1 1/2026] │ │
│  │                   ▲               │   │                  ~~~~~~~~~~~~ │ │
│  │                   │               │   │                  ▲ (Red Wavy) │ │
│  │  [Yellow Highlight Box around     │   │                               │ │
│  │   exact scan coordinates]         │   │ [Click word to open editor]   │ │
│  └───────────────────────────────────┘   └───────────────────────────────┘ │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
                   [ Interactive Token Correction Popover ]
                     • Original OCR: "15/1 1/2026" (Conf: 54%)
                     • Corrected Input: [ 15/11/2026 ]
                     • Action Buttons: [ Accept As-Is ]  [ Save Correction ]
                                       │
                                       ▼
                   [ Backend Re-Grounding Engine ]
                     • Persists edit to `user_confirmations` & updates `documents`
                     • Re-runs `verify_structured_notice()`
                     • Updates Canonical 6 Fields, plain summaries & checklist
                                       │
                                       ▼
                   [ Verified Document Dossier Export ]
                     • Emits timestamped, cryptographically hashed audit trail
```

---

## 3. Detailed Component Specifications

### 3.1 Spatial Coordinate Mapping & Page Geometry
To ensure that clicking a word in the text pane highlights the exact physical pixels on the scan:
1. **Coordinate Normalization:** The backend emits natural pixel coordinates $[x_1, y_1, x_2, y_2]$ based on natural image dimensions $W_{nat} \times H_{nat}$.
2. **Responsive Percentage Translation:** The frontend modal translates coordinates into responsive CSS percentages:
   $$\text{left} = \frac{x_1}{W_{nat}} \times 100\%, \quad \text{top} = \frac{y_1}{H_{nat}} \times 100\%$$
   $$\text{width} = \frac{x_2 - x_1}{W_{nat}} \times 100\%, \quad \text{height} = \frac{y_2 - y_1}{H_{nat}} \times 100\%$$
   This ensures that zooming (from 50% to 300%) or viewing on mobile maintains pixel-perfect alignment.

### 3.2 Evidence-Based Red Zigzag Underlining (No Speculative Flags)
A word token receives an interactive red zigzag underline **only** if one of the following deterministic criteria is met:
1. **Low OCR Confidence:** Tesseract or RapidOCR reports confidence score $<65.0\%$.
2. **Intra-Word Character Anomaly:** Word contains split numbers, illegal punctuation adjacent to numerals (e.g. `2026.11`), or un-repaired Devanagari ligatures.
3. **LLM Fact-Grounding Uncertainty:** The downstream extraction tagged this specific span as `uncertain` due to vague phrasing (e.g. `"before sunset"`).

*Rule: High-confidence words ($\ge 85.0\%$) with verified source grounding are never underlined.*

### 3.3 Interactive Correction Popover (`OCRTokenEditorModal.tsx`)
When a citizen clicks an underlined word:
- The left document pane smoothly pans and centers on the corresponding scan bounding box.
- An editing popover appears above the clicked token displaying:
  - **Extracted Text:** Read-only original OCR output.
  - **Confidence Badge:** Color-coded chip (e.g. `52% (Low Confidence)`).
  - **Proposed Value:** Input field pre-filled with the current string or regex-repaired suggestion.
  - **Accept / Reject / Confirm Buttons:**
    - `Accept Extracted`: Confirms the OCR was correct despite low confidence.
    - `Save Correction`: Saves the citizen's typed correction.
    - `Cancel`: Discards without modification.

### 3.4 Correction Memory & Audit Trail
Every correction is recorded in the SQLite database (`user_confirmations` table):
- `document_id`: UUID of the notice.
- `token_index`: Index of the corrected word in the transcript.
- `original_value`: Exact string output by OCR engine.
- `corrected_value`: Citizen's validated replacement.
- `user_id`: Authenticated user ID (or `"guest"`).
- `timestamp`: UTC ISO timestamp.

### 3.5 Re-Grounding Pipeline
When a token correction is committed:
1. The backend updates the stored document text in `documents.text_content`.
2. The revised text is piped to `verify_structured_notice(structured_notice, updated_text)`.
3. If the corrected token resolves an uncertain date or eligibility cutoff, the field status is updated from `flagged_uncertain` to `verified`.
4. Dependent plain-language summaries and action checklist steps are re-generated via `server.py` in under 200ms.

---

## 4. Required API Endpoints & Contracts

### 4.1 Update OCR Token Endpoint
- **Route:** `POST /api/ocr/correct-token`
- **Request Body:**
  ```json
  {
    "document_id": "doc_9a8b7c6d",
    "token_index": 42,
    "original_text": "15/1 1/2026",
    "corrected_text": "15/11/2026",
    "field_name": "deadline"
  }
  ```
- **Response:**
  ```json
  {
    "status": "success",
    "document_id": "doc_9a8b7c6d",
    "updated_field_status": "verified",
    "quality_score": 96.4,
    "active_uncertain_count": 0
  }
  ```

### 4.2 Re-Ground Document Endpoint
- **Route:** `POST /api/documents/{document_id}/re-ground`
- **Description:** Re-evaluates all 6 canonical fields and checklist items against the user-corrected full text.

### 4.3 Export Verified Document Dossier
- **Route:** `POST /api/export/verified-dossier`
- **Description:** Emits a comprehensive Markdown/PDF audit package containing the original image, extracted OCR transcript, side-by-side correction ledger, and final verified action plan with SHA-256 integrity seal.
