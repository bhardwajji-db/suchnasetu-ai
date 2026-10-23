# Implementation Summary: SochnaSetu AI Multilingual Notice-to-Action Engine
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** Hack Day 2026 — PS02  
**Timestamp:** 2026-10-24  
**Scope:** Architecture overview, component decoupling, persistence layer, multi-format pipeline, and UI integration.

---

## 1. Architectural Mission

The goal of this overhaul is to elevate SochnaSetu AI into an enterprise-grade, judge-ready, accessibility-first civic intelligence assistant. The upgraded system provides:

1. **Complete 10-Language Internationalization:** Full coverage across English and 9 major Indian constitutional languages (`hi`, `bn`, `ta`, `te`, `mr`, `gu`, `pa`, `kn`, `ur`), with bidirectional text layout support (RTL for Urdu).
2. **Decoupled Language Architecture:** Strict separation between **Document Source Language** (with automated script classification, lexical scoring, and manual user override) and **Output Explanation Language** (in which summaries, checklists, and answers are synthesized).
3. **Multi-Format Ingestion Pipeline:** Robust, zero-dependency ingestion of `.txt`, `.pdf` (searchable and scanned), `.docx` (Office Open XML element tree parser), and image formats (`.png`, `.jpg`, `.jpeg`, `.webp`, `.tif`, `.tiff`).
4. **Persistent SQLite Database Engine:** Zero-overhead, WAL-enabled ACID storage in `data/suchnasetu.db` managing documents, extracted facts, analyses, persistent checklist toggle states, user confirmations, Q&A records, and demo registry surviving reboots.
5. **Interactive 32-Document Demo Library:** A curated, judge-accessible library with >=3 authentic notices per language, covering 30 real-world civic categories with a persistent frontend catalogue view.

---

## 2. Key Architecture Diagram

```mermaid
flowchart TD
    subgraph Frontend ["React 19 + TypeScript + Vite"]
        UI[10-Language UI & RTL Switcher]
        Bar[Source & Output Language Selector]
        Lib[Demo Library Catalog & Search]
        WS[Notice Intelligence Workspace]
        Tabs[Grounded Facts • Summary • Checklist • Q&A]
    end

    subgraph API ["FastAPI Backend (Port 8000)"]
        IngestAPI[/api/ingest & /api/ocr]
        DetectAPI[/api/language/detect]
        AnalyzeAPI[/api/analyze]
        DemoAPI[/api/demo-library]
        ChecklistAPI[/api/checklist/toggle]
        StorageAPI[/api/documents]
    end

    subgraph Ingestion ["Ingestion & Preprocessing"]
        FormatValidator[Security & Magic Byte Validator]
        DOCXParser[DOCX ElementTree Parser]
        PDFParser[pypdf + PyMuPDF Extraction]
        OCREngine[Tesseract OCR Engine]
        LangDetector[Script & Lexical Classifier]
    end

    subgraph Intelligence ["Local AI Inference (100% Offline)"]
        Gemma[Ollama gemma4:latest 8.0B]
        Grounder[Grounded Facts Extractor]
        Summarizer[Plain Language Generator]
        Translator[Multilingual Localized Engine]
    end

    subgraph Storage ["Persistent SQLite DB (WAL Mode)"]
        DB[(data/suchnasetu.db)]
        Uploads[(data/uploads/)]
        Fixtures[(tests/fixtures/demo_library/)]
    end

    UI --> Bar
    Bar --> DetectAPI
    UI --> Lib --> DemoAPI
    UI --> WS --> AnalyzeAPI
    WS --> ChecklistAPI

    IngestAPI --> FormatValidator --> DOCXParser & PDFParser & OCREngine
    FormatValidator --> LangDetector
    AnalyzeAPI --> Gemma --> Grounder --> Summarizer --> Translator
    AnalyzeAPI --> DB
    ChecklistAPI --> DB
    DemoAPI --> Fixtures & DB
    IngestAPI --> Uploads & DB
```

---

## 3. Core Component Breakdown

### 3.1 10-Language Internationalization
- **Dictionaries:** Typed, comprehensive JSON/TS translation maps in `frontend/src/i18n/locales/` (`en`, `hi`, `bn`, `ta`, `te`, `mr`, `gu`, `pa`, `kn`, `ur`).
- **Context:** React `I18nProvider` that reacts instantaneously to language switches without page reloads, updates `document.documentElement.lang` and `dir`, and persists preferences in `localStorage`.
- **RTL Support:** Urdu (`ur`) activates Right-to-Left document flow, with mirrored layouts, padding adjustments, and correct bidirectional font rendering.

### 3.2 Decoupled Language Pipeline
- **Source Language:** Detected using unicode block regex scanning (`Devanagari`, `Bengali`, `Gurmukhi`, `Gujarati`, `Tamil`, `Telugu`, `Kannada`, `Arabic/Urdu`, `Latin`) followed by lexical frequency scoring. User override dropdown allows manual correction.
- **Output Language:** User-selectable target language for plain-language summaries, action checklists, and Q&A answers.
- **Grounding Integrity:** Canonical extracted values and verbatim evidence quotes remain unmutated in the original document language, guaranteeing 100% source truthfulness.

### 3.3 Multi-Format Ingestion
- **DOCX Parsing:** Built without external bloat using Python's standard library `zipfile` and `xml.etree.ElementTree`, extracting paragraphs and tables from `word/document.xml`.
- **Image Formats:** Supported `.png`, `.jpg`, `.jpeg`, `.webp`, `.tif`, `.tiff` via PIL / Pillow preprocessing (grayscale, Otsu thresholding, contrast enhancement) and Tesseract OCR.
- **PDF Extraction:** Dual-mode extraction using `pypdf` for digital text streams and fallback OCR for scanned PDFs.

### 3.4 Persistent Database Engine (`src/notice2action/storage/db.py`)
- **Engine:** SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`), enforcing foreign keys and ACID transactions.
- **Schema:**
  - `documents`: Stores raw text, sha256 checksums, source language, detected language, confidence, and file paths.
  - `analyses`: Stores structured notice JSON, 6-core fields, localized summary, action checklist, and duration.
  - `checklist_items`: Manages individual step completion status persistently.
  - `user_confirmations`: Stores human audit corrections for uncertain facts.
  - `qa_interactions`: Logs question-answer history and supporting quotes.
  - `demo_registry`: Catalogues all demo library entries.
  - `app_settings`: Stores key-value system settings.
- **Restart Verification:** All checklist toggles and analysis artifacts persist across complete backend reboots.

### 3.5 Demo Library
- **Location:** `tests/fixtures/demo_library/`
- **Catalog:** 32 authentic civic notices in 10 languages across 30 categories with a verified `manifest.json`.
- **Frontend UI:** Searchable, filterable gallery in `DemoLibraryView.tsx` with instant "Load into Assistant" routing.
