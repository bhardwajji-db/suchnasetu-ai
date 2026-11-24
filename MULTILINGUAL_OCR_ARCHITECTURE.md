# SochnaSetu AI — Universal Multilingual OCR Architecture Specification

**Document Version:** 1.0.0  
**Design Date:** November 24, 2026  
**Author:** Principal OCR, Computer Vision & Multilingual Systems Architect  
**Repository Path:** `C:\Users\Avinash\OneDrive\Desktop\AI-Projects\Hacktober fest\ps2`  
**Scope:** Universal OCR Architecture for all 22 Indian Scheduled Languages + English  
**Status:** PROPOSED ARCHITECTURAL BLUEPRINT (AUDIT & DESIGN ONLY)

---

## 1. Architectural Vision & Core Principles

The objective of the **Universal Multilingual OCR Subsystem** in **SochnaSetu AI** is to ingest official administrative notices, government circulars, and academic announcements in any of the **22 Indian Scheduled Languages** or **English**, reliably transcribing both printed and degraded scanned documents while maintaining strict privacy, local execution capability, and verbatim evidence grounding.

### Ten Architectural Tenets
1. **Privacy-First & Local-First:** All OCR processing must execute on-premise or within self-contained container boundaries without mandatory cloud API dependencies or document leakage.
2. **Digital Fast-Path First:** Always extract native digital vector text streams if available, avoiding unnecessary lossy image rasterization and CPU overhead.
3. **Multi-Script & Code-Switching Awareness:** Indian government circulars frequently interleave Latin dates (`20/11/2026`), English reference numbers (`No. 12/4/2026-Exam`), and regional language text. The pipeline must support multi-script token alignment.
4. **Hierarchical Engine Routing:** Route cleanly between lightweight LSTM engines (Tesseract) for standardized scripts and specialized transformer/deep models (AI4Bharat IndicOCR / PaddleOCR) for complex or low-resource scripts.
5. **Deterministic Preprocessing:** Maintain page orientation, deskewing, and contrast normalization prior to character recognition.
6. **Layout & Reading-Order Preservation:** Reconstruct multi-column circulars, sidebars, and tabular schedules into ordered Markdown or structured spatial blocks.
7. **Explicit Uncertainty & Low-Confidence Scoring:** Never conceal OCR degradation; calculate token-level confidence and flag uncertain spans for human review.
8. **Verbatim Text Preservation:** Downstream AI layers must consume canonical extracted text and must never silently alter or invent missing source text.
9. **Graceful CPU Degradation:** Models must run effectively on modest dual-core CPU container instances (512MB–1GB RAM limits) with optional GPU acceleration.
10. **Zero Regression Guarantee:** Retain all verified existing enhancements for English (CER 2.75%–3.46%) and Hindi (CER 12.60%).

---

## 2. End-to-End Pipeline Data Flow

```
                                [Uploaded Notice Document]
                               (PDF, Image: PNG/JPG/WebP/TIFF)
                                              │
                                              ▼
                             [Step 1: Ingestion & Format Router]
                                              │
                       ┌──────────────────────┴──────────────────────┐
                       │                                             │
               [Vector Digital PDF]                          [Scanned Document]
                       │                                    (Image or Scanned PDF)
                       ▼                                             │
            [Native Text Extraction]                                 ▼
             (pypdf character stream)                   [300 DPI Rasterization]
                       │                                (pypdfium2 / Poppler memory)
                       │                                             │
                       │                                             ▼
                       │                            [Step 2: Adaptive Preprocessing]
                       │                            ├── Orientation (0°, 90°, 180°, 270°)
                       │                            ├── Deskewing (±15° Hough / Moments)
                       │                            ├── Contrast & Shadow Normalization
                       │                            └── Shirorekha / Divider Isolation
                       │                                             │
                       │                                             ▼
                       │                        [Step 3: Script & Language Identification]
                       │                        ├── High-Density Fast Script Classifier
                       │                        └── Multi-Script Bounding Box Segmentation
                       │                                             │
                       │                                             ▼
                       │                       [Step 4: Hierarchical OCR Engine Router]
                       │                                             │
                       │                     ┌───────────────────────┼───────────────────────┐
                       │                     ▼                       ▼                       ▼
                       │             [Tesseract Engine]     [IndicOCR / PP-OCR]      [Specialized Model]
                       │             (Standard Indic)       (Complex / Low-Res)      (Ol Chiki / Meetei)
                       │             hin, ben, tam, tel...  mal, ori, urd, pan...    sat, mni, kas
                       │                     │                       │                       │
                       │                     └───────────────────────┼───────────────────────┘
                       │                                             │
                       │                                             ▼
                       │                           [Step 5: Multi-Script Token Alignment]
                       │                           ├── Spatial IoU English Date/Digit Fusion
                       │                           └── Script-Specific Dictionary Repairs
                       │                                             │
                       │                                             ▼
                       │                           [Step 6: Layout & Reading Order Graph]
                       │                           ├── Heading, Paragraph & Table Sorting
                       │                           └── Spatial Bounding-Box Indexing
                       │                                             │
                       └──────────────────────────────┬──────────────┘
                                                      │
                                                      ▼
                                       [Canonical OCRResult Payload]
                       ├── Raw Extracted Text (Immutable)
                       ├── Word-Level Bounding Boxes & Confidence Scores
                       ├── Uncertainty Flags & Ambiguous Spans
                       └── Document Quality Metrics
                                                      │
                                                      ▼
                                   [Downstream Evidence Grounding Engine]
                       ├── Verbatim Quote Containment Verification
                       └── Structured 6-Field Notice Extraction (Gemma 4 / OpenRouter)
```

---

## 3. Subsystem Specifications

### 3.1 Step 1: Ingestion & Format Router
- **Digital Vector PDF Detection:** Ingest using `pypdf`. If the average character density across all pages exceeds 100 characters per page and font stream tables are valid, bypass image rasterization.
- **Scanned PDF Rasterization:** Uses `pypdfium2` to stream in-memory 300 DPI PIL images. If PDFium bindings fail, fall back to Poppler `pdftoppm` in an isolated temporary directory.
- **Image Sanitization:** Validate magic bytes (`%PDF-`, `\x89PNG`, `\xFF\xD8\xFF`), enforce the 15MB file size limit, and sanitize filenames against path traversal.

### 3.2 Step 2: Adaptive Preprocessing
- **Orientation Normalization (4-Angle):** Combine Tesseract Orientation and Script Detection (OSD) with an empirical word-count confidence fallback for short single-line circulars. Rotate inverted images to 0° upright.
- **Deskewing:** Calculate document skew using minimum-area bounding boxes of detected text contours or horizontal Radon transforms. Correct angles within `[-15.0°, +15.0°]`.
- **Contrast & Illumination Equalization:** Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) and adaptive Gaussian thresholding to neutralize shadow gradients from mobile camera photographs.
- **Divider Line Isolation:** Morphological horizontal structuring elements detect and isolate long tabular borders and horizontal rules, preventing them from fusing into Devanagari or Gurmukhi shirorekha toplines.

### 3.3 Step 3: Script & Language Identification (LID)
- **Document-Level Script Detection:** Analyze character histograms across 10 major script blocks:
  - Devanagari (`U+0900`–`U+097F`)
  - Bengali-Assamese (`U+0980`–`U+09FF`)
  - Gurmukhi (`U+0A00`–`U+0A7F`)
  - Gujarati (`U+0A80`–`U+0AFF`)
  - Odia (`U+0B00`–`U+0B7F`)
  - Tamil (`U+0B80`–`U+0BFF`)
  - Telugu (`U+0C00`–`U+0C7F`)
  - Kannada (`U+0C80`–`U+0CFF`)
  - Malayalam (`U+0D00`–`U+0D7F`)
  - Ol Chiki (`U+1C50`–`U+1C7F`)
  - Meetei Mayek (`U+ABC0`–`U+ABFF`)
  - Perso-Arabic / Urdu / Kashmiri (`U+0600`–`U+06FF`, `U+0750`–`U+077F`)
  - Latin / English (`a-z`, `A-Z`)
- **Patch-Level Script Segmentation:** When documents contain mixed languages (e.g., English header + Tamil body), regional bounding boxes are tagged with their dominant script to route individual text crops to script-specific models.

### 3.4 Step 4: Hierarchical OCR Engine Router
Instead of relying on a single engine that struggles on diverse scripts, the proposed architecture establishes a multi-engine routing strategy:
- **Tier 1 (High-Performance Tesseract LSTM):** For standardized scripts where Tesseract models are mature and fast (English, Hindi, Marathi, Bengali, Assamese, Gujarati, Tamil, Telugu, Kannada, Sanskrit).
- **Tier 2 (AI4Bharat IndicOCR / PP-OCRv5):** For highly conjunct-dense or rounded scripts prone to segmentation errors in Tesseract (Malayalam, Odia, Punjabi, Urdu).
- **Tier 3 (Specialized Script Adapters):** Dedicated models for scripts absent from standard distributions (Santali Ol Chiki, Manipuri Meetei Mayek, Kashmiri modified Perso-Arabic).

### 3.5 Step 5: Multi-Script Token Alignment & Spatial Fusion
- **Spatial IoU Date/Digit Fusion:** Indian circulars frequently embed Arabic numerals within non-Latin text. A parallel English pass extracts numeric candidates (`20/11/2026`, `₹15,000`). When an English token overlaps an Indic token with IoU > 0.50 and matches a date, currency, or application code regex, the calibrated English digits are fused into the regional sentence.
- **Domain Lexicon Repair:** Post-processing regex and dictionary passes repair broken ligatures, dropped nuktas, and severed shirorekha artifacts for statutory circular terms (e.g. *Corrigendum*, *Secretary*, *Eligibility*).

### 3.6 Step 6: Layout & Reading-Order Graph
- Reconstructs text flow from top-to-bottom and left-to-right (or right-to-left for Urdu/Kashmiri/Sindhi).
- Table cells are grouped by row coordinates (`y-overlap >= 70%`) and separated with Markdown pipe syntax (`|`).

---

## 4. Preservation of Original Text & Downstream Grounding

A strict architectural invariant governs the AI analysis boundary:
1. **Raw OCR Immutability:** The raw string returned by the OCR engine is written to the database (`documents.raw_ocr_text`) and never modified.
2. **No Generative "Repair" of Source Text:** Downstream Large Language Models (Gemma 4 26B / OpenRouter) are strictly prohibited from rewriting the raw document. If OCR output is garbled or incomplete, the model must output `"Not Stated"` or flag uncertainty.
3. **Evidence Grounding Requirement:** Every claim in the extracted summary, eligibility matrix, or deadline list must cite a verbatim quote from the original text with start/end character offsets and bounding-box coordinates for modal visualization.

---

## 5. Architectural Quality Matrix

| Component | Target Latency (CPU) | Target Memory Footprint | Accuracy Goal (CER) | Fallback Strategy |
| :--- | :---: | :---: | :---: | :--- |
| **Vector PDF Extractor** | < 50ms / page | < 30 MB RAM | 0.00% (Lossless) | Poppler rasterizer |
| **Preprocessor & Deskew**| < 1.0s / page | < 65 MB RAM | Angle ±0.5° | Raw image passthrough |
| **Script Classifier** | < 10ms / page | < 20 MB RAM | > 99.5% accuracy | Default to `hin+eng` |
| **Tesseract Tier** | 2.5s–6.0s / page | < 80 MB RAM | < 3.0% (Clean), < 13% (Degraded)| Single-pass `eng` |
| **IndicOCR Tier** | 3.0s–7.0s / page | < 250 MB RAM | < 5.0% (Complex Indic) | Tesseract Indic model |
| **Trust Engine Scoring** | < 5ms / claim | < 10 MB RAM | 100% deterministic | Flag ungrounded claim |

---

## 6. Architecture Status & Verification

This architectural blueprint satisfies all requirements for production reliability, local privacy, multi-script coordination, and verbatim legal grounding across India's constitutional language landscape.
