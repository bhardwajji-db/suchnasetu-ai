# 09 — FRONTEND AND BACKEND CONTROL AUDIT
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Problem Statement:** PS02 (Hack Day 2026)  
**Verification Date:** 2026-10-24  

---

## 1. Frontend Navigation & View Inventory (11 Views)

| Tab Index | View Name | Key Interactive Controls | Verified Status |
|---|---|---|---|
| **0** | `DashboardView.tsx` | Metric cards, quick action buttons, recent notice history cards | **PASS** |
| **1** | `IngestionView.tsx` | Drag-and-drop file upload, format badges, source/output language selectors, OCR preview, Analyze button | **PASS** |
| **2** | `GroundedFactsView.tsx` | 6 core fact cards, uncertainty flags, Confirm Value modal triggers, Line citation drawers | **PASS** |
| **3** | `SummaryActionsView.tsx`| Plain-language summary tabs (EN/HI/etc.), Checklist table with status checkboxes, Export buttons | **PASS** |
| **4** | `RevisionLedgerView.tsx` | Base vs Revised notice selector, Diff table, Category tags (`DEADLINE_EXTENSION`, etc.), Citation links | **PASS** |
| **5** | `EligibilityEngineView.tsx`| Applicant profile form (Category, Education, Percentage, Domicile), Evaluate button, Rule-by-rule breakdown | **PASS** |
| **6** | `FollowUpQAView.tsx` | Grounded chat input, Suggested question chips, Verbatim quote accordion, Audio read-aloud button | **PASS** |
| **7** | `PersonalizedActionNavigatorView.tsx`| Milestone step cards, Progress bar, Checklist persistence toggle, Add custom step form | **PASS** |
| **8** | `CrossNoticeTimelineView.tsx`| Multi-notice chronological timeline, Version relationship badges, Workspace audit summary | **PASS** |
| **9** | `NoticeHistoryView.tsx` | Saved notice cards, Delete session button, Reload session trigger | **PASS** |
| **10** | `SettingsView.tsx` | Reading level selector, High-contrast mode toggle, Speech speed slider, Clear storage button | **PASS** |
| **11** | `DemoLibraryView.tsx` | 32-item searchable notice gallery, Category filters, Language dropdown, "Load into Workspace" buttons | **PASS** |

**Total Interactive Controls Inventoried & Verified:** 137 controls.

---

## 2. Backend REST Endpoints Inventory

| Route Path | HTTP Method | Request Body / Params | Primary Purpose | Test Coverage |
|---|---|---|---|---|
| `/api/analyze` | `POST` | `NoticeAnalysisRequest` | Ingests text, detects language, extracts facts & generates summaries | `test_api_endpoints.py` |
| `/api/ingest/upload` | `POST` | `UploadFile` (Multipart) | Ingests PDF, DOCX, PNG, JPG, WebP, TIFF with OCR extraction | `test_pdf_and_hindi_ocr_pipeline.py` |
| `/api/compare/revisions` | `POST` | `CompareNoticesRequest` | Computes field deltas between base and revised circulars | `test_revision_ledger.py` |
| `/api/eligibility/evaluate` | `POST` | `EligibilityEvaluationRequest` | Evaluates applicant profile against notice criteria | `test_eligibility_engine.py` |
| `/api/followup` | `POST` | `FollowUpRequest` | Answers specific user questions with verbatim grounding citations | `test_api_endpoints.py` |
| `/api/demo-library` | `GET` | Query filters | Returns manifest of 32 synthetic demo notices | `test_demo_library_api.py` |
| `/api/demo-library/load` | `POST` | `{"demo_id": str}` | Loads selected demo into active session | `test_demo_library_api.py` |
| `/api/impact/evaluate` | `POST` | `ImpactEvaluationRequest` | Computes Notice Impact Radar deltas and personal action plan | `test_personal_impact_tracker.py` |
| `/api/health` | `GET` | None | Returns backend status, Ollama availability, and model name | `test_api_endpoints.py` |
