# SochnaSetu AI — Modern Frontend UI/UX Redesign Proposal

**Target Application:** `frontend/src/`  
**Role:** Senior React UI/UX Engineer & Design Systems Architect  

---

## 1. Design Vision: Premium Civic Document Intelligence

The current frontend is feature-complete and functional, but features a traditional tabbed layout where document viewing, fact cards, and AI chat are accessed across disjointed views.

The **Redesigned Interface** transitions SochnaSetu AI into an **Integrated Split-Screen Intelligence Workspace** reminiscent of modern developer and legal review platforms (such as Linear, VS Code, and Claude Artifacts):
- **Unified Split Workbench:** Citizens can view the original circular image or OCR transcript in the left pane while interacting with extracted facts, plain summaries, and grounded Q&A in the right pane simultaneously.
- **Cognitive Hierarchy:** High-priority items (Deadlines, Required Documents, and Eligibility status) command immediate focal attention with color-coded urgency indicators.
- **Zero-Flicker Transitions:** Asynchronous view loading with skeletons and lazy-loaded modules.

---

## 2. Design System & Typography Specifications

### 2.1 Typography Hierarchy
- **Primary Interface Font:** `Inter` (Variable font, weights 400, 500, 600, 700) for UI controls, navigation, and summaries.
- **Indic Devanagari Font:** `Noto Sans Devanagari` for native, rendering of Hindi vowels, halants, and conjuncts.
- **Code & OCR Monospace Font:** `JetBrains Mono` for raw OCR dumps, token indices, regex patterns, and line numbering.

### 2.2 Color Palettes & Dual-Theme Tokens

| Token Name | Light Civic Theme | Dark Midnight Navy Theme | Purpose |
|---|---|---|---|
| `--bg-canvas` | `#F8FAFC` (Slate 50) | `#0B1220` (Deep Navy) | Primary viewport background |
| `--bg-surface` | `#FFFFFF` (Pure White) | `#131E32` (Surface Navy) | Cards, modals, drawers |
| `--border-subtle` | `#E2E8F0` (Slate 200) | `#1E2E4A` (Muted Slate) | Dividers and card borders |
| `--text-primary` | `#0F172A` (Slate 900) | `#F8FAFC` (White/Silver) | Primary headings and text |
| `--text-muted` | `#64748B` (Slate 500) | `#94A3B8` (Slate 400) | Metadata, captions, quotes |
| `--brand-emerald` | `#08785D` (Civic Green)| `#10B981` (Vibrant Emerald)| Primary actions, verified badges |
| `--accent-teal` | `#0D9488` (Teal 600) | `#14B8A6` (Teal 400) | Highlights, secondary buttons |
| `--alert-danger` | `#DC2626` (Red 600) | `#EF4444` (Red 500) | Uncertain tokens, red wavy lines |
| `--alert-warning` | `#D97706` (Amber 600)| `#F59E0B` (Amber 500) | Approaching deadlines, caveats |

---

## 3. View-by-View Redesign Specifications

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ HEADER: Brand Logo • Live Model Badge • Language Selector • Profile / Guest Tag  │
├──────────────┬──────────────────────────────────┬────────────────────────────────┤
│ SIDEBAR      │ WORKBENCH PANE A                 │ WORKBENCH PANE B               │
│ (Collapsible)│ (Original Notice Scan / Text)    │ (AI Intelligence & Fact Cards) │
│              │                                  │                                │
│ • Dashboard  │ [ Image Preview / OCR Stream ]   │ [ 6 Canonical Fact Cards ]     │
│ • Ingest     │                                  │ • Issuing Authority            │
│ • Facts      │  • Zoom (50% - 300%)             │ • Reference ID                 │
│ • Checklist  │  • Red Wavy Underline Highlights │ • Filing Deadline              │
│ • Eligibility│  • Bounding Box Overlays         │ • Required Documents           │
│ • Timeline   │  • Search & Filter Spans         │                                │
│ • History    │                                  │ [ Interactive Grounded Q&A ]   │
│ • Settings   │                                  │ [ Citizen Action Checklist ]   │
└──────────────┴──────────────────────────────────┴────────────────────────────────┘
```

### View 1: Dashboard (`DashboardView.tsx`)
- **Redesign:** Executive overview showing summary metric cards (Urgency Level, Days Remaining until Deadline, Total Required Documents, OCR Document Quality Score).
- **Hero Alert:** Top urgent notice banner in high-contrast amber with a 1-click `"Download Citizen Action Slip"` button.

### View 2: Ingestion & Standalone OCR (`IngestionView.tsx`)
- **Redesign:** Two-stage drag-and-drop zone supporting drag-to-upload for PDFs and photos, or direct paste into a monospaced input.
- **Preflight Diagnostics:** Real-time client-side image resolution check (flags images under 150 DPI before upload) and instant MIME detection.

### View 3: Grounded Facts Workspace (`GroundedFactsView.tsx`)
- **Redesign:** Integrated split-screen. Left pane displays the zoomable original document; right pane displays the 6 canonical field cards.
- **Click-to-Highlight:** Clicking any fact card (e.g. `Deadline: 15/11/2026`) scrolls the left document pane directly to the exact scan coordinates and illuminates a golden-yellow focus ring.

### View 4: Plain Summary & Audio Actions (`SummaryActionsView.tsx`)
- **Redesign:** Split-tab card with Standard vs Easy-Read reading levels.
- **Audio Synthesizer Bar:** Sticky audio player at the base of the viewport with bilingual waveform animation, speed adjustment (0.75x, 1.0x, 1.25x), and sentence-by-sentence read-aloud highlighting.

### View 5: Revision Ledger & Corrigendum Diffing (`RevisionLedgerView.tsx`)
- **Redesign:** Visual side-by-side comparative diff showing Original Notice vs Corrigendum Notice with color-coded strike-throughs for cancelled clauses and emerald green highlights for extended deadlines.

### View 6: Eligibility Engine (`EligibilityEngineView.tsx`)
- **Redesign:** Interactive citizen profile form (Percentage Marks, Category, Age, Degree Enrollment). Evaluates citizen criteria against extracted notice conditions with pass/fail badges and explanatory citations.

### View 7: Follow-Up Q&A Assistant (`FollowUpQAView.tsx`)
- **Redesign:** Conversational chat interface strictly grounded in the notice text. Preloaded chip suggestions (`"What is the final deadline?"`, `"Is there an application fee?"`, `"Where do I submit?"`). Emits verified citation pills referencing exact line numbers.

### View 8: Personalized Action Navigator (`PersonalizedActionNavigatorView.tsx`)
- **Redesign:** Kanban-style or ordered timeline checklist with progress percentage bar, countdown timers for approaching deadlines, and document attachment indicators.

### View 9: Multi-Notice Timeline (`CrossNoticeTimelineView.tsx`)
- **Redesign:** Interactive chronological Gantt-style timeline showing notice lifecycle: Initial Announcement $\to$ Corrigendum 1 $\to$ Deadline Extension $\to$ Final Results.

### View 10: Notice History & Dossier Registry (`NoticeHistoryView.tsx`)
- **Redesign:** Grid/List view with thumbnail cards, tag filters (Scholarship, Recruitment, Municipal), full-text search, and quick PDF export shortcuts.

### View 11: Demo Library (`DemoLibraryView.tsx`)
- **Redesign:** Showcase gallery categorized by language (Hindi, Bengali, Tamil, Telugu, Marathi, English) and civic scenario (Scholarship, Municipal Water Advisory, UPSC Notice). Includes one-click `"Load & Analyze"` cards.

### View 12: Settings & Hardware Diagnostics (`SettingsView.tsx`)
- **Redesign:** Dedicated hardware monitoring dashboard showing OCR Engine status (Tesseract vs RapidOCR), active inference model, CPU memory footprint, and accessibility configuration toggles.
