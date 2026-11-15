# SochnaSetu AI (PS02) — Complete Project Feature Inventory
**Document Version:** 1.0.0  
**Project:** SochnaSetu AI — Notice-to-Action Accessibility Assistant  
**Hack Day Track:** PS02 — Notice Understanding & Accessibility  
**Inventory Status:** 100% Fully Discovered, Implemented, Connected, and Verified  
**Audit Date:** October 24, 2026  

---

## Executive Feature Catalog

SochnaSetu AI provides a complete, privacy-preserving, air-gapped solution that transforms complex legal, academic, and administrative notices into grounded, accessible actions for all citizens.

Every feature listed below is **fully implemented**, **connected to the interactive React frontend**, backed by **deterministic FastAPI backend endpoints**, and verified with **automated pytest, vitest, and Playwright tests**.

---

## Master Feature Table

| Feature ID | Feature Name | Primary Implementation | UI Component / View | API Route | Test Suite | Completeness |
|---|---|---|---|---|---|---|
| **FEAT-01** | Multi-Format Document Ingestion | `notice2action/ingestion.py` | `IngestionView.tsx` | `/api/ingest/text`, `/api/ingest/upload` | `test_pdf_ingestion.py` | 100% Complete |
| **FEAT-02** | Adaptive Bilingual OCR Pipeline | `notice2action/ocr.py` | `IngestionView.tsx` | `/api/ocr` | `test_hindi_ocr.py` | 100% Complete |
| **FEAT-03** | Six Core Legal Notice Extraction | `notice2action/analysis.py` | `GroundedFactsView.tsx` | `/api/analyze` | `test_services_and_six_fields.py` | 100% Complete |
| **FEAT-04** | Semantic Fact Grounding & Attribution | `notice2action/grounding.py` | `GroundedFactsView.tsx` | `/api/analyze` | `test_evidence_trust_engine.py` | 100% Complete |
| **FEAT-05** | Plain-Language Summary (Tri-Level) | `notice2action/summary.py` | `SummaryActionsView.tsx` | `/api/summary/reading-level` | `test_phase_d_notice_scenarios.py` | 100% Complete |
| **FEAT-06** | Hindi Accessibility Translation | `notice2action/translation.py` | `SummaryActionsView.tsx` | `/api/analyze` | `test_phase_d_notice_scenarios.py` | 100% Complete |
| **FEAT-07** | Grounded Action Checklist Synthesis | `notice2action/checklist.py` | `SummaryActionsView.tsx` | `/api/analyze` | `test_personalized_action_navigator.py` | 100% Complete |
| **FEAT-08** | Checklist State Persistence | `NoticeContext.tsx` | `ActionChecklistTable.tsx` | N/A (Client Storage) | `ActionChecklistTable.test.tsx` | 100% Complete |
| **FEAT-09** | iCalendar (.ics) Calendar Export | `notice2action/schemas.py` | `SummaryActionsView.tsx` | `/api/export/ics` | `test_api_endpoints.py` | 100% Complete |
| **FEAT-10** | Markdown Action Plan (.md) Export | `server.py` | `SummaryActionsView.tsx` | `/api/export/markdown` | `test_api_endpoints.py` | 100% Complete |
| **FEAT-11** | Human-in-the-Loop Fact Correction | `server.py` | `ConfirmationModal.tsx` | `/api/confirm-fact` | `ConfirmationModal.test.tsx` | 100% Complete |
| **FEAT-12** | Notice-Grounded Follow-Up Q&A | `notice2action/followup.py` | `FollowUpQAView.tsx` | `/api/followup` | `test_live_gemma4.py` | 100% Complete |
| **FEAT-13** | Epistemic Absent-Topic Refutation | `notice2action/followup.py` | `FollowUpQAView.tsx` | `/api/followup` | `test_phase_d_notice_scenarios.py` | 100% Complete |
| **FEAT-14** | Universal Evidence Trust Inspector | `trust_engine.py` | `EvidenceInspectorDrawer.tsx` | `/api/trust/verify-evidence` | `test_evidence_trust_engine.py` | 100% Complete |
| **FEAT-15** | Explainable Eligibility Engine | `eligibility_engine.py` | `EligibilityEngineView.tsx` | `/api/eligibility/evaluate` | `test_eligibility_engine.py` | 100% Complete |
| **FEAT-16** | Age Limit & Category Relaxation Logic | `eligibility_engine.py` | `EligibilityEngineView.tsx` | `/api/eligibility/evaluate` | `test_eligibility_engine.py` | 100% Complete |
| **FEAT-17** | Multi-Notice Revision Ledger | `revision_engine.py` | `RevisionLedgerView.tsx` | `/api/revision-ledger/compare` | `test_revision_ledger.py` | 100% Complete |
| **FEAT-18** | Personal Impact Change Tracker | `impact_engine.py` | `RevisionLedgerView.tsx` | `/api/impact/evaluate` | `test_personal_impact_tracker.py` | 100% Complete |
| **FEAT-19** | Personalized Action Navigator | `action_navigator_service.py`| `PersonalizedActionNavigatorView.tsx`| `/api/actions/generate` | `test_personalized_action_navigator.py` | 100% Complete |
| **FEAT-20** | Live Deadline Countdown Intelligence | `action_navigator_service.py`| `PersonalizedActionNavigatorView.tsx`| `/api/actions/generate` | `test_feature_comprehensive_matrix.py` | 100% Complete |
| **FEAT-21** | Cross-Notice Temporal Timeline | `relationship_engine.py` | `CrossNoticeTimelineView.tsx` | `/api/relationships/detect` | `test_cross_notice_intelligence.py` | 100% Complete |
| **FEAT-22** | Persistent Notice History & Cache | `NoticeContext.tsx` | `NoticeHistoryView.tsx` | N/A (Client Storage) | Unit Vitest Suite | 100% Complete |
| **FEAT-23** | System Health & Diagnostics Preflight| `notice2action/config.py` | `SettingsView.tsx` | `/api/health` | `test_api_endpoints.py` | 100% Complete |
| **FEAT-24** | Multi-Provider LLM Switcher | `server.py` | `SettingsView.tsx` | `/api/provider/switch` | `test_multi_provider_llm.py` | 100% Complete |
| **FEAT-25** | Local Gemma 4 Air-Gapped Inference | `llm/ollama_client.py` | Ingestion & Q&A Views | `/api/analyze`, `/api/followup` | `test_live_gemma4.py` | 100% Complete |
| **FEAT-26** | WCAG 2.1 AA Accessibility Modes | `NoticeContext.tsx` | Global Header & Settings | N/A (CSS & DOM) | `Header.test.tsx` | 100% Complete |
| **FEAT-27** | Assistive Voice Guidance Bar | `NoticeContext.tsx` | `VoiceGuidanceBar.tsx` | `/api/tts` (Local Web Speech) | `VoiceGuidanceBar.test.tsx` | 100% Complete |
| **FEAT-28** | Adversarial Prompt Injection Defense | `notice2action/security.py` | API Middleware & Ingestion | `/api/analyze` | `test_phase_d_notice_scenarios.py` | 100% Complete |

---

## Detailed Functional Specifications

### 1. Multi-Format Ingestion & Adaptive OCR
- Supports pasted text, UTF-8 text files, multi-page PDFs, and images (PNG, JPG, JPEG, WEBP).
- Adaptive image enhancement: automatically applies grayscale conversion, contrast normalization, and adaptive thresholding to maximize OCR readability on degraded physical scans.
- Dual-engine OCR pipeline with Tesseract (`eng`, `hin`, `eng+hin`) and fallback handling.

### 2. Six Core Legal Notice Fields & Semantic Grounding
- Extracts the six critical legal notice parameters mandated by Indian administrative standards:
  1. Issuing Authority or Department
  2. Notice / Reference Number
  3. Notice Issuance Date
  4. Intended Recipient / Candidate Category
  5. Main Subject / Purpose
  6. Action Required & Final Deadline
- Enforces strict verbatim evidence quotes. Any field not explicitly stated in the document is labeled `NOT_STATED` with certainty level `NOT_STATED`.

### 3. Explainable Applicant Eligibility Engine
- Pure Python deterministic rule evaluation eliminating LLM calculation errors.
- Automatic extraction of qualification requirements, minimum aggregate percentage marks, and age cutoff boundaries.
- Reservation category relaxation modeling (+3 years for OBC, +5 years for SC/ST).
- Returns explainable verdicts (`PASS`, `FAIL`, `UNKNOWN`) accompanied by exact textual citations.

### 4. Multi-Notice Revision Ledger & Personal Impact Tracker
- Field-by-field diff comparison between original circulars and subsequent corrigenda/amendments.
- Detects deadline extensions, fee revisions, qualification shifts, and examination center modifications.
- Personal Impact Engine classifies whether changes are beneficial (e.g. deadline extended, fees reduced), adverse (e.g. fees increased), or neutral.

### 5. Personalized Action Navigator
- Synthesizes personalized roadmaps with dependency-aware ordering.
- Live deadline countdown badges (`Due today`, `Due soon`, `Upcoming`, `Past deadline`, `Superseded by corrigendum`).
- Allows users to check off tasks, record private notes, view evidence proof, and click verified official submission links.

### 6. Universal Evidence Trust Inspector
- Sliding drawer providing instant visual proof for any fact, summary sentence, or eligibility requirement.
- Highlights exact text spans in the original notice with line numbers and character offsets.
- Distinguishes between `VERIFIED`, `UNCERTAIN_OCR`, and `UNVERIFIED` claims.

### 7. Accessibility, Voice Guidance & Privacy
- High-contrast color palette conforming to WCAG 2.1 AA (4.5:1 text contrast ratio).
- OpenDyslexic font support and large text scaling (115%).
- Persistent audio player providing variable rate playback (0.75x–1.25x) using local browser Web Speech API.
- 100% offline air-gapped execution with zero cloud telemetry or paid API reliance.
