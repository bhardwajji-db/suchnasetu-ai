# Changelog — SuchnaSetu AI

All notable changes to the SochnaSetu AI platform are documented in this file.

---

## [2.0.0] — 2026-10-24

### Added
- **10-Language UI:** Full translation dictionaries for `en`, `hi`, `bn`, `ta`, `te`, `mr`, `gu`, `pa`, `kn`, and `ur`.
- **Urdu Dynamic RTL:** Bidirectional layout switching with text mirroring for Urdu script.
- **Multilingual Intelligence Bar:** Decoupled Document Source Language from AI Output Explanation Language in `IngestionView.tsx`.
- **32-Notice Demo Library:** Interactive gallery in `DemoLibraryView.tsx` with search, category filters, and backend load API.
- **SQLite WAL Persistence:** Relational database at `data/suchnasetu.db` with 6 tables (`documents`, `structured_notices`, `action_tasks`, `deadlines`, `reminders`, `revisions`).
- **Notice Impact Radar:** 5-question multi-dimensional notice evaluation engine.
- **Cross-Device Testing:** Playwright tests across 6 device viewports.
- **Fictional Demo Evaluation:** Automated ground-truth evaluation script and fixture for `fake_notice_for_testing.docx`.

### Fixed
- Fixed TypeScript compile errors (TS6133) in `frontend/src/i18n/index.ts`.
- Fixed Follow-Up Q&A localized fallback bug overwriting valid English answers.
- Fixed brittle substring assertions in `tests/test_live_gemma4.py`.
- Fixed Windows file locking `[WinError 32]` during SQLite temp directory teardown.
- Fixed relative path calculation error in `ingestion.py`.
- Fixed undefined `HINDI_MARKERS` variable in `language_detection.py`.
- Fixed missing `PROJECT_ROOT` import in `server.py` demo library load endpoint.
- Fixed Applicant Profile schema 422 error by adding extra field tolerance and aliases in `schemas.py`.
- Fixed missing `overall_verdict` attribute in `EligibilityAssessment`.
- Fixed `RevisionEntry.category` mapping to semantic types (`DEADLINE_EXTENSION`, `FEE_CHANGE`).
- Fixed adversarial security test assertion in `test_synthetic_demo_suite.py`.
- Fixed non-interactive delay in `start_all.bat`.

### Security
- Verified zero cloud telemetry and 100% offline local inference via Ollama.
- Parameterized all SQLite database queries.
- Sanitized file upload paths to prevent directory traversal.
- Neutralized adversarial prompt injection and DAN jailbreak attempts.
