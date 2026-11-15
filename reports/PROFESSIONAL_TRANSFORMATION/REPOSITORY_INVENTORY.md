# COMPLETE REPOSITORY INVENTORY & ARCHITECTURAL CLASSIFICATION
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  
**Audit Scope:** Entire Repository Tree  

---

## 1. Directory Structure Overview

```
ps2/
├── frontend/                          # React 19 + TypeScript + Vite Client Application
│   ├── src/
│   │   ├── components/                # Reusable UI Controls & Modals (14 components)
│   │   ├── context/                   # Global React State & Notice Context
│   │   ├── i18n/                      # 10-Language Translation Engine & Dictionaries
│   │   ├── services/                  # Typed API Client & Axios Transports
│   │   ├── test/                      # Vitest Component & Unit Tests (14 suites)
│   │   ├── types/                     # TypeScript API Contracts & Interfaces
│   │   └── views/                     # 11 Main Navigation Workspace Views
│   ├── package.json                   # Frontend dependencies (React 19, Lucide, Tailwind)
│   └── vite.config.ts                 # Vite bundler configuration
│
├── src/notice2action/                 # Core Python / FastAPI Backend Service
│   ├── api/                           # REST Endpoints, routers, and server lifecycle
│   │   ├── server.py                  # Primary FastAPI Application (1,356 lines)
│   │   └── __init__.py                # Package exports
│   ├── llm/                           # Local LLM Integration Layer (Ollama / Gemma 4)
│   │   ├── factory.py                 # Multi-provider LLM Factory
│   │   ├── gemini_client.py           # Gemini Client adapter (optional)
│   │   ├── huggingface_client.py      # HuggingFace Client adapter (optional)
│   │   └── openrouter_client.py       # OpenRouter Client adapter (optional)
│   ├── services/                      # Domain Business Engines & Extraction Services
│   │   ├── action_navigator_service.py# Milestone Checklist Generator
│   │   ├── eligibility_engine.py      # Explainable Rules Evaluator
│   │   ├── evidence_service.py        # Verbatim Citation & Trust Inspector
│   │   ├── impact_engine.py           # Notice Impact Radar Deltas
│   │   ├── relationship_engine.py     # Base vs Corrigendum Notice Linker
│   │   ├── revision_engine.py         # Semantic Revision Ledger Engine
│   │   ├── session_store.py           # In-Memory Active Session Cache
│   │   ├── trust_engine.py            # Evidence Grounding Trust Scorer
│   │   └── workspace_service.py       # Cross-Notice Timeline & Audit Service
│   ├── storage/                       # Local-First Persistent SQLite Storage
│   │   ├── db.py                      # DatabaseManager (WAL mode, 6 tables)
│   │   └── __init__.py                # Storage exports
│   ├── analysis.py                    # NoticeAnalyzer: 6 Core Fields & Facts
│   ├── checklist.py                   # Action Checklist Normalization
│   ├── config.py                      # Application Configuration & Env Settings
│   ├── evaluator.py                   # OCR Quality & Uncertainty Detector
│   ├── followup.py                    # Grounded Q&A Assistant Engine
│   ├── grounding.py                   # Verbatim Citation Validator
│   ├── ingestion.py                   # Multi-Format Parser (.txt, .pdf, .docx, images)
│   ├── language_detection.py          # Character & Script Frequency Detector
│   ├── ocr.py                         # Tesseract OCR & Image Preprocessing Pipeline
│   ├── schemas.py                     # Pydantic v2 Models (758 lines)
│   ├── security.py                    # Input Sanitization & Prompt Injection Filter
│   ├── summary.py                     # Plain-Language Summarization
│   ├── translation.py                 # Multilingual Text Translation
│   └── tts.py                         # Text-to-Speech Engine
│
├── tests/                             # Automated Test Suites (pytest)
│   ├── fixtures/                      # Test Data & Ground Truth Fixtures
│   │   ├── demo_library/              # 32 Synthetic Notices (all formats & languages)
│   │   └── demo_notices/              # 5 Hackathon Synthetic Scenario Notices
│   ├── test_api_endpoints.py          # REST API Endpoints Contract Tests
│   ├── test_cross_notice_intelligence.py # Timeline & Corrigendum Tests
│   ├── test_demo_library.py           # Manifest & Fixture Integrity Tests
│   ├── test_demo_library_api.py       # Demo Library Loading API Tests
│   ├── test_eligibility_engine.py     # Explainable Eligibility Evaluation Tests
│   ├── test_evidence_trust_engine.py  # Evidence Citation & Grounding Tests
│   ├── test_feature_comprehensive_matrix.py # Comprehensive Feature Matrix Tests
│   ├── test_feature_edge_cases.py     # Boundary & Malformed Inputs Tests
│   ├── test_hindi_ocr.py              # Hindi Devanagari OCR Pipeline Tests
│   ├── test_live_gemma4.py            # 5 Live Ollama Gemma 4 Inference Prompts
│   ├── test_multi_provider_llm.py     # Provider Switching Tests
│   ├── test_negative_and_edge_cases.py# Negative Input Validation Tests
│   ├── test_ollama_integration.py     # Ollama Host & Model Verification Tests
│   ├── test_pdf_and_hindi_ocr_pipeline.py # Scanned PDF & OCR Tests
│   ├── test_pdf_ingestion.py          # PDF Text Extraction Tests
│   ├── test_personal_impact_tracker.py# Notice Impact Radar Tests
│   ├── test_personalized_action_navigator.py # Action Navigator Tests
│   ├── test_phase_d_notice_scenarios.py # Phase D Scenarios Tests
│   ├── test_playwright_react_frontend.py # 6-Viewport Playwright E2E Tests
│   ├── test_reliability_and_privacy.py # Privacy & Zero Cloud Leakage Tests
│   ├── test_revision_ledger.py        # Semantic Revision Ledger Engine Tests
│   ├── test_services_and_six_fields.py# Core Fact Services Tests
│   ├── test_storage_db.py             # SQLite WAL Persistence Tests
│   ├── test_structured_notice_regression.py # Pydantic Model Schema Tests
│   ├── test_synthetic_demo_fixtures.py# Fixture Integrity Tests
│   ├── test_synthetic_demo_suite.py   # 5 Live End-to-End Demo Tests
│   └── test_unit_pipeline.py          # Core Pipeline Unit Tests
│
├── reports/                           # Comprehensive Verification Audits
│   ├── FINAL_SYSTEM_VERIFICATION/     # 16 Full-System Test & Release Reports
│   └── PROFESSIONAL_TRANSFORMATION/   # Engineering Quality & Inventory Audits
│
├── scripts/                           # Utility & Packaging Scripts
│   ├── create_fake_notice.py          # Fictional Demo DOCX Generator
│   ├── evaluate_fictional_demo.py     # Fictional Demo QA Evaluator
│   ├── generate_demo_library.py       # 32 Demo Fixture Generator
│   ├── generate_ground_truth_dataset.py # Ground Truth Dataset Generator
│   ├── package_release.ps1            # Release Bundling Script
│   ├── run_ground_truth_accuracy_audit.py # Ground Truth Accuracy Auditor
│   └── setup.ps1                      # Windows Setup Automation Script
│
├── data/                              # Local Runtime Storage (Git Ignored)
│   ├── suchnasetu.db                  # SQLite 3 ACID Database (WAL Mode)
│   ├── uploads/                       # Uploaded Document Store
│   └── .gitkeep                       # Empty directory placeholder
│
├── .gitignore                         # Comprehensive Git Exclusions
├── pyproject.toml                     # Python Package & Dependencies (uv/pip)
├── README.md                          # Primary Project Documentation
├── SETUP.md                           # Windows Development Setup Guide
└── start_all.bat                      # All-in-One Service Launcher
```

---

## 2. File-by-File Quality Audit

| Subsystem | File Path | Language | Quality Status | Proposed Action |
|---|---|---|---|---|
| **Frontend Root** | `frontend/src/App.tsx` | TSX | Clean, wraps `I18nProvider` & `NoticeProvider` | Maintain |
| **Frontend Router** | `frontend/src/components/ApplicationLayout.tsx` | TSX | Clean, renders Header, Sidebar, and active View | Maintain |
| **Frontend State** | `frontend/src/context/NoticeContext.tsx` | TSX | Comprehensive (839 lines), supports all 10 langs | Maintain |
| **Frontend I18n** | `frontend/src/i18n/I18nContext.tsx` | TSX | Clean context with dynamic RTL direction hook | Maintain |
| **Frontend I18n** | `frontend/src/i18n/locales/*.ts` (10 files) | TS | 10 typed dictionaries, 65 keys each | Maintain |
| **Frontend View** | `frontend/src/views/IngestionView.tsx` | TSX | Contains multilingual intelligence bar | Maintain |
| **Frontend View** | `frontend/src/views/DemoLibraryView.tsx` | TSX | 32-notice gallery with search & filters | Maintain |
| **Frontend View** | `frontend/src/views/RevisionLedgerView.tsx` | TSX | Semantic revision comparison viewer | Maintain |
| **Frontend View** | `frontend/src/views/EligibilityEngineView.tsx` | TSX | Rule-by-rule profile evaluator | Maintain |
| **Backend API** | `src/notice2action/api/server.py` | Python | 1,356 lines, REST endpoints, error handling | Maintain |
| **Backend Schemas**| `src/notice2action/schemas.py` | Python | 758 lines, Pydantic v2 models, field validators | Maintain |
| **Backend Storage**| `src/notice2action/storage/db.py` | Python | SQLite 3 WAL manager, 6 tables, connection pooling | Maintain |
| **Backend Services**| `src/notice2action/services/*.py` (9 files) | Python | Specialized domain logic engines | Maintain |
| **Backend Ingestion**| `src/notice2action/ingestion.py` | Python | Robust multi-format parsing (.txt, .pdf, .docx, imgs) | Maintain |
| **Backend OCR** | `src/notice2action/ocr.py` | Python | Tesseract OCR pipeline with thresholding | Maintain |
