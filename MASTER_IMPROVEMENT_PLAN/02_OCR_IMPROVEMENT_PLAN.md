# SochnaSetu AI — OCR Improvement Plan & Technical Specification

**Target Component:** `src/notice2action/ocr.py`, `src/notice2action/schemas.py`, `src/notice2action/api/server.py`  
**Role:** Senior OCR Research Engineer & Computer Vision Architect  

---

## 1. Architectural Objective

Transform SochnaSetu AI's OCR engine from a brittle, single-threaded Tesseract pipeline with overfitted domain hacks into a **robust, high-throughput, document-type-aware OCR system**.

Target metrics:
- **English CER:** Maintain $<0.5\%$ on clean documents.
- **Hindi / Mixed Devanagari CER:** Reduce from $2.75\%$ to $<1.5\%$.
- **Processing Latency:** Reduce average per-page OCR latency from $6.3\text{s}$ to $<1.2\text{s}$ on standard CPU hardware.
- **Orientation Recovery:** 100% automated recovery on 90°, 180°, and 270° rotated documents regardless of line count.
- **Token Integrity:** Zero split dates or split numbers (e.g., $15/11/2026$, never $15/1\ 1/2026$).

---

## 2. Investigation of Current Deficiencies & Algorithmic Solutions

### 2.1 Tesseract OSD Orientation Failure
- **Current File & Function:** `src/notice2action/ocr.py` $\to$ `detect_image_orientation(image: Image.Image)` (lines 63–91)
- **Problem:** Tesseract's `image_to_osd()` requires a minimum character count threshold. On brief notices, posters, or certificates with $<15$ text lines, it throws an internal exception (`Too few characters. Wait for more`) and silently returns rotation `0°`.
- **Algorithmic Solution:**
  Implement a **Dual-Stage Orientation Estimator**:
  1. *Stage 1 (Fast OSD):* Attempt `image_to_osd()`. If successful and confidence $\ge 15.0$, apply the rotation.
  2. *Stage 2 (4-Quadrant Aspect Ratio & Radon Edge Density Fallback):* If Stage 1 fails, compute the horizontal and vertical projection profiles of edge maps (Sobel/Canny). Since printed Latin and Devanagari text inherently exhibits dense horizontal line banding (shirorekha lines) compared to vertical banding, test 0° and 90° orientations:
     $$\text{Orientation} = \arg\max_{\theta \in \{0^\circ, 90^\circ\}} \text{Var}\left(\text{Proj}_\theta(I)\right)$$
     If aspect ratio $W > H$ on a circular known to be portrait (or vice versa), test 90° rotation and execute a lightweight 1-second OCR confidence check on the upper header region to establish upright orientation definitively.

### 2.2 RapidOCR Engine Integration & Missing Dependencies
- **Current File & Function:** `src/notice2action/ocr.py` $\to$ `RapidOCREngine` (lines 1180–1260) and `pyproject.toml`
- **Problem:** `RapidOCREngine` is already coded as a clean `BaseOCREngine` subclass, but fails at runtime with `ImportError: RapidOCR is not installed in the environment`. It currently lacks word bounding box extraction, confidence calibration, and Hindi models.
- **Algorithmic Solution:**
  1. Add `rapidocr-onnxruntime>=1.3.8` to `pyproject.toml` and `requirements.txt`.
  2. Implement comprehensive token packaging in `RapidOCREngine.extract_text`:
     - Map each detection polygon `item[0]` $[[x_1, y_1], [x_2, y_2], [x_3, y_3], [x_4, y_4]]$ into a standard axis-aligned bounding box $[x_{min}, y_{min}, x_{max}, y_{max}]$.
     - Extract word text and detection confidence $C \in [0, 100]$.
     - Return populated `word_boxes` and `image_dimensions` matching the `TesseractOCREngine` contract.
  3. Wire RapidOCR as the default primary engine when installed, maintaining Tesseract as an air-gapped zero-dependency fallback.

### 2.3 Hindi & Bilingual OCR Accuracy
- **Current File & Function:** `src/notice2action/ocr.py` $\to$ `fused_multilingual_tesseract` (lines 771–912)
- **Problem:** Tesseract's single `hin+eng` pass frequently mistakes English numerals for Devanagari numerals or introduces garbled characters at script boundaries.
- **Algorithmic Solution:**
  1. **Script-Specific Token Assignment:** Rather than blindly accepting Tesseract's `hin+eng` output, inspect Unicode character blocks. If a token's bounding box has Latin characters or ASCII digits, cross-reference with the pure `eng` pass.
  2. **Shirorekha Line & Matra Preservation:** Low-contrast scans erode the top horizontal headline (*shirorekha*). In `preprocess_image_pipeline`, apply morphology opening with a flat $3 \times 1$ horizontal structuring element before thresholding to reinforce character connectivity.

### 2.4 Numeral Spacing Errors
- **Current File & Function:** `src/notice2action/ocr.py` $\to$ post-processing & `src/notice2action/grounding.py`
- **Problem:** Spatial IoU fusion merges split bounding boxes, introducing spaces into numbers (e.g. `15/1 1/2026`, `Rs. 5 0,0 0 0`).
- **Algorithmic Solution:**
  Implement a deterministic token cleanup regex pass in `clean_and_repair_gazette_text` (and generalized notice repair):
  ```python
  # 1. Collapse spaces between digits separated by slashes or hyphens
  text = re.sub(r'(\d{1,2})\s*([/-])\s*(\d{1,2})\s*([/-])\s*(\d{2,4})', r'\1\2\3\4\5', text)
  # 2. Collapse internal single-space breaks inside 4-digit years and long numerals
  text = re.sub(r'(?<=\b\d)\s+(?=\d\b)', '', text)
  # 3. Collapse spaces in currency amounts: 'Rs. 5 0 0' -> 'Rs. 500'
  text = re.sub(r'(Rs\.?|INR|₹)\s*(\d+)\s+(\d+)', r'\1 \2\3', text)
  ```

### 2.5 Gazette-Specific Hardcoded Vocabulary
- **Current File & Function:** `src/notice2action/ocr.py` (lines 204–248, 843–850)
- **Problem:** The repository contains hardcoded strings (`"अपराजिता सारंगी"`, `"11011/1/2016"`) that explicitly overfit to a single test sample.
- **Algorithmic Solution:**
  1. Remove hardcoded names from the core `fused_multilingual_tesseract` loop.
  2. Create a generic `GazettePostProcessor` that triggers **only** when `category == "GAZETTE"` or when statutory masthead indicators are detected.
  3. Replace literal name matching with generic regex patterns for Indian administrative signatories:
     ```python
     # Matches any name followed by Joint Secretary / Director / Commissioner
     m = re.search(r'([A-Z\u0900-\u097F\s\.\-]{3,40}),\s*(?:संयुक्त सचिव|Joint Secretary|Under Secretary|Director)', text)
     ```

### 2.6 Word-Level Confidence & Spatial Bounding Boxes
- **Current File & Function:** `src/notice2action/ocr.py` $\to$ `OCRResult`
- **Enhancement:** Ensure every single extracted word carries:
  - `text: str`
  - `box: [x1, y1, x2, y2]` in natural image pixel space
  - `confidence: float` (0.0 to 100.0)
  - `line_number: int`
  - `page_number: int`
  - `is_uncertain: bool` (true if confidence < 65.0 or anomaly detected)
  This enables the frontend to render precise word-level bounding boxes and red zigzag underlines.

### 2.7 Table Structure Extraction
- **Current File & Function:** `src/notice2action/ocr.py`
- **Enhancement:** Multi-column and tabular notices (e.g. eligibility grade matrices, fee schedules) lose row-column relationships when flattened into 1D text.
- **Implementation Design:**
  Implement a lightweight heuristic **Grid Projection Analyzer**:
  - Detect horizontal and vertical ruling lines via morphological kernels ($1 \times 30$ and $30 \times 1$).
  - Calculate grid intersections to form cells.
  - Group word bounding boxes into their respective row-column cell coordinates.
  - Export structured markdown tables (`| Column 1 | Column 2 |`) to the LLM context, preventing column interleaving.

---

## 3. Exact File & Function Modification Matrix

| File Path | Function / Class | Nature of Modification | Priority |
|---|---|---|:---:|
| `pyproject.toml` & `requirements.txt` | Dependencies manifest | Add `rapidocr-onnxruntime>=1.3.8` | P1 |
| `src/notice2action/ocr.py` | `detect_image_orientation` | Implement 4-quadrant edge density fallback for short notices | P0 |
| `src/notice2action/ocr.py` | `RapidOCREngine.extract_text`| Implement bounding boxes, confidence, and ONNX execution | P1 |
| `src/notice2action/ocr.py` | `fused_multilingual_tesseract`| Add intra-digit space normalization; remove hardcoded names | P1 |
| `src/notice2action/ocr.py` | `extract_regional_signatory_block`| Generalize signatory detection via regex patterns | P1 |
| `src/notice2action/schemas.py` | `OCRResponse` / `OCRResult` | Add `word_boxes: List[WordBox]` schema with confidence | P1 |
| `src/notice2action/grounding.py` | `extract_critical_tokens` | Relax date regex to tolerate intra-numeral space variations | P1 |
| `src/notice2action/api/server.py` | `ocr_endpoint` | Expose word-level confidence and bounding coordinates in API | P1 |
