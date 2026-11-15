# 01. CODEBASE INVENTORY & ARCHITECTURE — SOCHNASETU AI

**Root Directory:** `.`  
**Repository Branch:** `main`  
**Head Commit:** `26ca54f`

---

## 1. Directory Tree & Classification

```
ps2/
├── .dockerignore                            # Docker build exclusions
├── .env.example                             # Environment template (offline defaults)
├── .gitignore                               # Git exclusion rules
├── Dockerfile                               # Multi-stage production container build
├── Procfile                                 # PaaS deployment entrypoint
├── README.md                                # Comprehensive project documentation
├── docker-compose.yml                       # App + Ollama multi-container orchestration
├── package.json                             # Root Node package configuration
├── pyproject.toml                           # Python package, tool & pytest configuration
├── run_app.bat                              # Quick-start script delegating to start_all.bat
├── start_all.bat                            # Full-stack dev launcher (Vite + FastAPI + Ollama)
├── start_production.bat                     # Single-port production launcher (Port 8000)
├── start_production.sh                      # Linux / macOS production bash launcher
│
├── assets/
│   ├── screenshots/                         # 34 high-resolution workflow & viewport screenshots
│   └── tessdata/                            # Tesseract trained models (eng, hin, osd)
│
├── docs/
│   ├── DEPLOYMENT.md                        # Enterprise 4-mode deployment manual
│   └── PRODUCTION_CHECKLIST.md              # Production sign-off checklist
│
├── frontend/                                # React 19 + TypeScript + Vite SPA
│   ├── dist/                                # Compiled production distribution
│   ├── src/
│   │   ├── components/                      # 18 Modular UI components
│   │   │   ├── ActionChecklistTable.tsx     # Checklist items, categories & CSV export
│   │   │   ├── AnalysisProgressModal.tsx    # Processing pipeline visualizer
│   │   │   ├── ApplicationLayout.tsx        # Responsive layout shell with sidebar & header
│   │   │   ├── ConfirmationModal.tsx        # Human-in-the-loop fact confirmation dialog
│   │   │   ├── EvidenceInspectorDrawer.tsx  # Verbatim quote & line attribution drawer
│   │   │   ├── FactCard.tsx                 # Core fact display with trust indicators
│   │   │   ├── FileDropzone.tsx             # Multi-format drag-and-drop upload
│   │   │   ├── GroundedQAChat.tsx           # Grounded Q&A chat with voice input
│   │   │   ├── Header.tsx                   # Top navigation bar, language switcher, dark mode
│   │   │   ├── MetricCard.tsx               # Analytics metric cards
│   │   │   ├── MobileBottomNav.tsx          # Mobile navigation bar with touch targets
│   │   │   ├── NoticeBuffer.tsx             # Text buffer & demo loader
│   │   │   ├── OCRPanel.tsx                 # Image preview & OCR status controls
│   │   │   ├── OriginalNoticeViewerModal.tsx# Verbatim raw notice viewer with text search
│   │   │   ├── PlainLanguageSummaryView.tsx # Summary answers to 7 core questions
│   │   │   ├── Sidebar.tsx                  # Collapsible desktop navigation bar
│   │   │   ├── StaleWarningBanner.tsx       # Re-analysis prompt when buffer changes
│   │   │   ├── VoiceGuidanceBar.tsx         # Floating accessibility audio player
│   │   │   └── VoiceInputButton.tsx         # Microphone speech-to-text button
│   │   ├── context/
│   │   │   └── NoticeContext.tsx            # Global state store for notices, facts & checklists
│   │   ├── i18n/
│   │   │   ├── I18nContext.tsx              # React Context for language & direction
│   │   │   ├── languages.ts                 # Metadata for 10 constitutional Indian languages
│   │   │   ├── types.ts                     # Translation key schemas
│   │   │   └── [en,hi,bn,gu,kn,mr,pa,ta,te,ur].ts # Individual language translation tables
│   │   ├── services/
│   │   │   ├── api.ts                       # Backend REST client bindings
│   │   │   └── apiClient.ts                 # Typed fetch client with error handling
│   │   ├── test/                            # 17 Vitest test suites
│   │   └── views/                           # 12 Primary feature views
│   │       ├── CrossNoticeTimelineView.tsx  # Multi-notice chronological timeline
│   │       ├── DashboardView.tsx            # System diagnostic overview & stats
│   │       ├── DemoLibraryView.tsx          # 32-notice multi-language demo browser
│   │       ├── EligibilityEngineView.tsx    # Interactive applicant profile evaluation
│   │       ├── FollowUpQAView.tsx           # Dedicated follow-up question interface
│   │       ├── GroundedFactsView.tsx        # 6 Core legal notice facts display
│   │       ├── IngestionView.tsx            # Primary document upload & OCR screen
│   │       ├── NoticeHistoryView.tsx        # SQLite-persisted saved circulars
│   │       ├── PersonalizedActionNavigatorView.tsx # Prerequisite-ordered action roadmap
│   │       ├── RevisionLedgerView.tsx       # Corrigendum semantic diff & relationship detector
│   │       ├── SettingsView.tsx             # Provider diagnostics & configuration
│   │       └── SummaryActionsView.tsx       # Simplified summary & action checklist
│
├── reports/                                 # Evaluation reports, accuracy datasets & logs
│   ├── COMPLETE_PROJECT_AUDIT/              # Comprehensive 18-part audit documentation
│   ├── GROUND_TRUTH_ACCURACY_AUDIT/         # Multi-document accuracy evaluation dataset
│   ├── ps02_evaluation_results.json         # Ground truth evaluation against synthetic notice
│   └── system_feature_verification.json     # Machine-readable feature verification results
│
├── scripts/                                 # Verification & generation utilities
│   ├── audit_buttons.py                     # Interactive UI button checker
│   ├── create_fake_notice.py                # Synthetic DOCX notice generator
│   ├── evaluate_fictional_demo.py           # 10-Question fictional evaluation runner
│   ├── evaluate_ground_truth.py             # Ground truth accuracy auditor
│   ├── generate_demo_library.py             # 32-item demo notice dataset compiler
│   ├── generate_ground_truth_dataset.py     # Ground truth fixture generator
│   ├── preflight.py                         # System health & OCR preflight validator
│   ├── run_ground_truth_accuracy_audit.py   # Comprehensive multi-document OCR/LLM auditor
│   └── verify_all_features.py               # 20-Feature end-to-end master verification suite
│
├── src/notice2action/                       # Core Python backend package
│   ├── analysis/                            # Notice analysis & fact extraction
│   │   ├── notice_analyzer.py               # LLM prompt orchestrator & JSON parser
│   │   ├── six_fields.py                    # 6 core legal fields extractor
│   │   └── uncertainty_detector.py          # Tentative phrasing & OCR noise detector
│   ├── api/                                 # FastAPI REST server & routing
│   │   ├── models.py                        # Pydantic request / response schemas
│   │   └── server.py                        # 43 REST endpoints + static SPA mount
│   ├── evidence/                            # Evidence grounding & session management
│   │   ├── evidence_service.py              # Line-indexed verbatim evidence finder
│   │   └── session_store.py                 # Thread-safe local file session store
│   ├── llm/                                 # Multi-provider LLM integration layer
│   │   ├── base.py                          # Base LLM client interface
│   │   ├── factory.py                       # LLM provider selector factory
│   │   ├── gemini_client.py                 # Google Gemini REST client
│   │   ├── huggingface_client.py            # Hugging Face inference client
│   │   ├── ollama_client.py                 # Local Ollama client (Gemma 4 default)
│   │   └── openrouter_client.py             # OpenRouter OpenAI-compatible client
│   ├── ocr/                                 # Optical Character Recognition pipeline
│   │   ├── preprocessing.py                 # Grayscale, binarization & deskewing
│   │   ├── rapidocr_engine.py               # RapidOCR fallback engine
│   │   └── tesseract.py                     # Tesseract v5.4 engine with Hindi support
│   ├── services/                            # Domain services
│   │   ├── action_navigator_service.py      # Prerequisite blocking & roadmap service
│   │   ├── cross_notice_service.py          # Cross-circular registry & conflict detector
│   │   ├── eligibility_engine.py            # Deterministic applicant eligibility evaluation
│   │   ├── revision_engine.py               # Corrigendum semantic diff & relationship service
│   │   ├── storage_db.py                    # SQLite persistence service
│   │   ├── timeline_service.py              # Chronological event sequencing
│   │   ├── translation_service.py           # Multi-language text translator
│   │   └── tts_service.py                   # Privacy-hardened offline TTS service
│   ├── checklist.py                         # Grounded action checklist generator
│   ├── config.py                            # Pydantic environment configuration
│   ├── followup.py                          # Grounded Q&A assistant & absent info policy
│   ├── ingestion.py                         # Multi-format file ingestion (PDF, DOCX, TXT)
│   ├── schemas.py                           # Core Pydantic data schemas
│   ├── security.py                          # Adversarial prompt injection defense
│   └── summary.py                           # Plain-language accessible summary generator
│
└── tests/                                   # 27 Comprehensive backend test files
    ├── fixtures/                            # Authoritative test notices, images & docx
    ├── test_api_endpoints.py                # Core REST API endpoint tests
    ├── test_cross_notice_intelligence.py    # Cross-notice timeline & conflict tests
    ├── test_demo_library.py                 # Demo catalog manifest integrity tests
    ├── test_demo_library_api.py             # Demo catalog REST API tests
    ├── test_eligibility_engine.py           # Eligibility evaluation unit tests
    ├── test_evidence_trust_engine.py        # Trust engine verbatim matching tests
    ├── test_feature_comprehensive_matrix.py # Comprehensive feature matrix tests
    ├── test_feature_edge_cases.py           # Boundary conditions & edge case tests
    ├── test_hindi_ocr.py                    # Hindi OCR & Devanagari traineddata tests
    ├── test_live_gemma4.py                  # Live Gemma 4 Ollama integration tests
    ├── test_multi_provider_llm.py           # Multi-provider failover tests
    ├── test_negative_and_edge_cases.py      # Malformed inputs & adversarial tests
    ├── test_ollama_integration.py           # Local Ollama client health & timeout tests
    ├── test_pdf_and_hindi_ocr_pipeline.py   # PDF rendering & bilingual OCR tests
    ├── test_pdf_ingestion.py                # PDF document ingestion tests
    ├── test_personalized_action_navigator.py# Action roadmap dependency tests
    ├── test_personal_impact_tracker.py      # Corrigendum profile impact tests
    ├── test_phase_d_notice_scenarios.py     # Real-world notice scenarios
    ├── test_playwright_react_frontend.py    # Playwright responsive viewport tests
    ├── test_reliability_and_privacy.py      # Privacy & data isolation tests
    ├── test_revision_ledger.py              # Revision comparison tests
    ├── test_services_and_six_fields.py      # 6 core fields extraction tests
    ├── test_storage_db.py                   # SQLite persistence across restart tests
    ├── test_structured_notice_regression.py # Structured notice schema regression tests
    ├── test_synthetic_demo_fixtures.py      # 8 Canonical synthetic demo fixtures tests
    ├── test_synthetic_demo_suite.py         # 5 Canonical demo notice workflow tests
    └── test_unit_pipeline.py                # 25-Point master unit pipeline tests
```

---

## 2. Technology Stack

- **Backend Runtime:** Python 3.11.15
- **Web Framework:** FastAPI 0.115.0 + Starlette 0.41.2
- **ASGI Server:** Uvicorn 0.32.0 (running on `0.0.0.0:8000`)
- **Data Schemas & Validation:** Pydantic v2.9.2
- **Database:** SQLite 3 (`suchnasetu.db`)
- **Frontend Framework:** React 19.0.0
- **Language / Build Tool:** TypeScript 5.7.3 + Vite 8.3.4
- **CSS / Styling:** TailwindCSS 3.4.17 + PostCSS
- **Testing Tools:** Pytest 9.1.1 + Vitest 5.0.5 + Playwright 1.58.0
- **Local AI Engine:** Ollama 0.40.3 with Google Gemma 4 (`gemma4:latest`, 9.6 GB)
- **Local OCR Engine:** Tesseract OCR v5.4.0.20240606 (`eng`, `hin`, `osd`)
