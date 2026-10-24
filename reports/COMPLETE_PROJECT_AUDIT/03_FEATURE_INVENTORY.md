# 03. COMPREHENSIVE FEATURE INVENTORY — SOCHNASETU AI

This inventory catalogs every capability, service, and user interface module discovered and verified within SochnaSetu AI.

---

| Feature ID | Feature Name | Primary Implementation Files | Dependencies | Status |
| :--- | :--- | :--- | :--- | :---: |
| **FEAT-01** | Multi-Format Document Ingestion | `src/notice2action/ingestion.py`, `FileDropzone.tsx` | `pypdf`, `python-docx`, `PIL` | **PASS** |
| **FEAT-02** | Local Tesseract OCR Engine | `src/notice2action/ocr/tesseract.py`, `OCRPanel.tsx` | Tesseract v5.4.0 executable | **PASS** |
| **FEAT-03** | Devanagari Hindi OCR | `assets/tessdata/hin.traineddata`, `test_hindi_ocr.py` | Local `hin.traineddata` | **PASS** |
| **FEAT-04** | Constitutional Language Detection | `src/notice2action/services/translation_service.py` | Python standard library | **PASS** |
| **FEAT-05** | Six Core Notice Fields Extraction | `src/notice2action/analysis/six_fields.py`, `FactCard.tsx` | Gemma 4 / Regex Fallback | **PASS** |
| **FEAT-06** | Verbatim Evidence Grounding | `src/notice2action/evidence/evidence_service.py` | Sub-second line indexer | **PASS** |
| **FEAT-07** | Human-in-the-Loop Fact Confirmation | `ConfirmationModal.tsx`, `POST /api/confirm` | SQLite / Session Store | **PASS** |
| **FEAT-08** | 3-Tier Reading Level Selector | `src/notice2action/summary.py`, `SummaryActionsView.tsx` | Gemma 4 / Deterministic | **PASS** |
| **FEAT-09** | Grounded Conversational Q&A | `src/notice2action/followup.py`, `GroundedQAChat.tsx` | Gemma 4 + Evidence Index | **PASS** |
| **FEAT-10** | Truthful Absent Info Policy | `src/notice2action/followup.py` (Policy Gate) | Strict grounding rule | **PASS** |
| **FEAT-11** | Adversarial Injection Defense | `src/notice2action/security.py` | Regex + Boundary Isolation | **PASS** |
| **FEAT-12** | Explainable Eligibility Engine | `src/notice2action/services/eligibility_engine.py` | Deterministic Python engine | **PASS** |
| **FEAT-13** | Category-Based Age/Marks Relaxation | `src/notice2action/services/eligibility_engine.py` | Statutory quota rules | **PASS** |
| **FEAT-14** | Personalized Action Navigator | `src/notice2action/services/action_navigator_service.py` | Dependency DAG sorter | **PASS** |
| **FEAT-15** | Multi-Notice Revision Ledger | `src/notice2action/services/revision_engine.py` | Semantic diff comparator | **PASS** |
| **FEAT-16** | Corrigendum Relationship Detection | `src/notice2action/services/revision_engine.py` | Citation pattern matcher | **PASS** |
| **FEAT-17** | Personal Impact Change Tracker | `src/notice2action/services/revision_engine.py` | Profile delta evaluator | **PASS** |
| **FEAT-18** | Cross-Notice Registry & Timeline | `src/notice2action/services/cross_notice_service.py` | Chronological event sorter | **PASS** |
| **FEAT-19** | Circular Contradiction Engine | `src/notice2action/services/cross_notice_service.py` | Multi-document validator | **PASS** |
| **FEAT-20** | 32-Item Multi-Language Demo Catalog | `src/notice2action/api/server.py`, `DemoLibraryView.tsx` | Synthetic demo registry | **PASS** |
| **FEAT-21** | 3 Canonical Hackathon Demos | `tests/fixtures/demo_*.txt`, `NoticeBuffer.tsx` | Fictional fixture files | **PASS** |
| **FEAT-22** | Original Notice Document Viewer | `OriginalNoticeViewerModal.tsx` | React Modal + Clipboard API | **PASS** |
| **FEAT-23** | RFC 5545 Calendar .ICS Export | `src/notice2action/api/server.py` (`/api/export/ics`) | Standard Python datetime | **PASS** |
| **FEAT-24** | Formatted Markdown Action Export | `src/notice2action/api/server.py` (`/api/export/markdown`)| Markdown template engine | **PASS** |
| **FEAT-25** | Air-Gapped Offline TTS Engine | `src/notice2action/services/tts_service.py` | Serverless / Cloud-blocked | **PASS** |
| **FEAT-26** | Voice Guidance Player | `frontend/src/components/VoiceGuidanceBar.tsx` | Web Speech API | **PASS** |
| **FEAT-27** | Hands-Free Speech Recognition | `frontend/src/components/VoiceInputButton.tsx` | Web Speech Recognition API | **PASS** |
| **FEAT-28** | Multilingual UI (10 Languages + RTL) | `frontend/src/i18n/`, `Header.tsx` | Custom i18n store | **PASS** |
| **FEAT-29** | SQLite Persistence Across Restarts | `src/notice2action/services/storage_db.py` | SQLite 3 | **PASS** |
| **FEAT-30** | Unified Single-Port Serving | `src/notice2action/api/server.py` (`StaticFiles` + SPA) | FastAPI + Uvicorn | **PASS** |
| **FEAT-31** | Responsive Multi-Device UI | `frontend/src/index.css`, TailwindCSS | CSS Flexbox & CSS Grid | **PASS** |
| **FEAT-32** | Multi-Provider Failover Layer | `src/notice2action/llm/factory.py` | OpenRouter, Gemini, HF | **PASS** |
