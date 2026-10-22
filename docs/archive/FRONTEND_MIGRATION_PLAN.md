# Frontend Migration Plan: Streamlit to React + Vite + Tailwind CSS
**Project:** Notice2Action AI (PS02 — Notice-to-Action Accessibility Assistant)  
**Author:** Senior Full-Stack & Systems Architect  
**Date:** October 20, 2026  
**Status:** APPROVED FOR EXECUTION  

---

## 1. Executive Summary & Migration Objectives

The goal of this migration is to transition the frontend of **Notice2Action AI** from Streamlit to a production-grade, enterprise-ready **React + TypeScript + Vite + Tailwind CSS** single-page application (SPA), while:
1. **Preserving 100% of Python backend logic, OCR pipelines, local Gemma 4 model inference, Pydantic schemas, and security boundaries.**
2. **Eliminating Streamlit rendering limitations** (rerun race conditions, sandboxed iframes, DOM re-rendering overhead).
3. **Establishing a clean, typed REST API layer** using **FastAPI** on Python 3.11 that directly wraps the existing business modules without duplicating domain logic.
4. **Providing a responsive, dark navy & electric blue SaaS dashboard** matching modern legal-tech and competition standards.
5. **Guaranteeing 100% on-device privacy** with zero cloud API dependencies, zero paid keys, and offline resilience.
6. **Maintaining complete backward compatibility** so the original Streamlit application (`app.py`) remains 100% functional and recoverable.

---

## 2. Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────┐
│             React 19 + TypeScript + Vite               │
│               Tailwind CSS + Lucide Icons              │
│               React Router v7 / State Store            │
│         (Port 5173 - http://localhost:5173)            │
└──────────────────────────┬─────────────────────────────┘
                           │ Typed HTTP / JSON / Multipart
                           ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI REST Compatibility Layer           │
│        (Port 8000 - http://127.0.0.1:8000)             │
│            CORS enabled for localhost:5173             │
└────────┬─────────────────┬───────────────────┬─────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────────┐ ┌───────────────┐ ┌───────────────────┐
│ Tesseract OCR   │ │ Notice2Action │ │ Local Ollama      │
│ v5.4.0 (Local)  │ │ Domain Engine │ │ (gemma4:latest)   │
│ PIL preprocess  │ │ Schemas & Safe│ │ Port 11434        │
└─────────────────┘ └───────────────┘ └───────────────────┘
```

### Frontend Specifications:
- **Framework:** React 19 + TypeScript (Strict Mode)
- **Bundler:** Vite 6
- **Styling:** Tailwind CSS v4 / v3 with custom dark navy palette:
  - App Background: `#0B0F19` (Deep Obsidian Navy)
  - Card / Surface: `#111827` (Card Surface) with `#1F2937` borders
  - Accents / Primary: `#2563EB` & `#3B82F6` (Electric Blue)
  - Success / Certainty: `#10B981` (Emerald)
  - Warning / Ambiguity: `#F59E0B` (Amber)
  - Error / Conflict: `#EF4444` (Ruby)
- **Icons:** `lucide-react`
- **Routing:** `react-router-dom`
- **Testing:** `vitest` + `@testing-library/react` + Playwright E2E browser tests

### Backend REST Layer:
- **Framework:** FastAPI + Uvicorn (ASGI)
- **Port:** `8000` (`http://127.0.0.1:8000`)
- **Direct Engine Imports:**
  - `notice2action.config` -> System diagnostics & preflight checks
  - `notice2action.ocr` -> Image preprocessing & Tesseract execution
  - `notice2action.ingestion` -> Text & upload validation
  - `notice2action.analysis` -> NoticeAnalyzer & Gemma 4 extraction
  - `notice2action.grounding` -> Quote location & fact verification
  - `notice2action.summary` -> 7-question plain-language summaries
  - `notice2action.checklist` -> Sequential actionable checklist & RFC 5545 iCalendar
  - `notice2action.translation` -> Bilingual Hindi translation & entity auditing
  - `notice2action.followup` -> Grounded Q&A assistant
  - `notice2action.tts` -> Read-aloud audio generation

---

## 3. Migration Roadmap by Phases

### Phase 1: Repository Audit & API Contract Documentation (Current)
- Complete audit of all Python functions and data flows.
- Author `FRONTEND_MIGRATION_PLAN.md`, `FRONTEND_API_CONTRACT.md`, and `FRONTEND_MIGRATION_STATUS.md`.

### Phase 2: FastAPI Adapter Implementation & Backend API Tests
- Create `src/notice2action/api/server.py` exposing all operations via clean REST routes.
- Add comprehensive pytest integration suite `tests/test_api_endpoints.py`.
- Verify all routes pass with 100% compliance to schemas.

### Phase 3: Frontend Project Initialization
- Scaffold `frontend/` using Vite with React + TypeScript template.
- Configure Tailwind CSS, Lucide icons, React Router, Vitest, and testing utilities.
- Configure Vite development proxy to route `/api/*` to `http://127.0.0.1:8000`.

### Phase 4: UI Design System & Reusable Components
- Develop high-contrast, accessible dark navy layout with electric blue accents.
- Build reusable UI atoms and molecules:
  - `ApplicationLayout`, `Sidebar`, `Header`, `SystemStatusBadge`
  - `MetricCard`, `FactCard`, `EvidenceQuoteBadge`, `CertaintyIndicator`
  - `FileDropzone`, `NoticeBuffer`, `ActionChecklist`, `QuestionAnswerPanel`
  - `StaleWarningBanner`, `LoadingSpinner`, `ToastNotification`

### Phase 5: View Implementations & Complete Feature Parity
- **View 1: Dashboard / Overview:** System health, quick metrics, quick-load sample fixtures.
- **View 2: Notice Ingestion & OCR:** Drag-and-drop upload, image preview, contrast filter, OCR execution, ground-truth text buffer with live character/line counters and SHA-256 fingerprinting.
- **View 3: Grounded Fact Breakdown:** 8 key dimensions with verbatim quotations, certainty status, and interactive human-in-the-loop confirmation.
- **View 4: Summary & Action Checklist:** Plain-language 7-question summaries, bilingual English/Hindi toggle, interactive completion checkboxes, and iCalendar/Markdown downloads.
- **View 5: Follow-Up Q&A:** Grounded chat assistant with 4 preset quick inquiry buttons, quote citations, and hallucination refusal.

### Phase 6: Frontend Testing (Vitest & React Testing Library)
- Unit and integration tests covering component rendering, routing, state changes, and API mocks.

### Phase 7: Playwright Multi-Viewport Acceptance Testing
- Real browser tests verifying all views across 6 viewports (1920×1080 down to 390×844) with 0 horizontal overflow.

### Phase 8: Packaging & Verification
- Document verified run commands for both services and package production bundle.
