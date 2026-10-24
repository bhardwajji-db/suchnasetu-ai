# 16. CHANGED FILES LOG & AUDIT MANIFEST — SOCHNASETU AI

This manifest details every modified, created, or deleted file across the project transformation.

---

| File Path | Action | Rationale |
| :--- | :---: | :--- |
| `src/notice2action/api/server.py` | Modified | Added single-port static serving (`/assets`) and catch-all SPA route with path traversal security. |
| `frontend/src/i18n/I18nContext.tsx` | Modified | Bound language state updates bidirectionally to `NoticeContext` and set HTML `dir` attribute. |
| `frontend/src/views/GroundedFactsView.tsx` | Modified | Added optional chaining and safe fallback empty states for uninitialized notices. |
| `Dockerfile` | Created | Production multi-stage build (Node 20 build -> Python 3.11-slim runtime with Tesseract). |
| `docker-compose.yml` | Created | Multi-container orchestration (App on 8000 + Ollama on 11434 with persistent volumes). |
| `.dockerignore` | Created | Excluded version control, node_modules, and cache artifacts from image builds. |
| `Procfile` | Created | PaaS entrypoint for cloud deployment (`uvicorn notice2action.api.server:app`). |
| `start_production.bat` | Created | Windows one-click production launcher with Wi-Fi IP detection. |
| `start_production.sh` | Created | Linux/macOS executable production bash launcher. |
| `docs/DEPLOYMENT.md` | Created | Comprehensive 4-mode deployment manual (Docker, Ubuntu VPS, Cloud PaaS, Windows). |
| `docs/PRODUCTION_CHECKLIST.md` | Created | Formal production readiness verification checklist. |
| `scripts/verify_all_features.py` | Created | Master 20-feature end-to-end verification suite. |
| `scripts/create_fake_notice.py` | Modified | Targeted generation strictly to `tests/fixtures/fake_notice_for_testing.docx`. |
| `run_app.bat` | Modified | Updated to delegate cleanly to `start_all.bat`. |
| `.env.example` | Modified | Documented all local and cloud configuration variables. |
| `fake_notice_for_testing.docx` (root) | Deleted | Removed duplicate file from root; canonical copy preserved in `tests/fixtures/`. |
| `frontend/src/assets/react.svg` | Deleted | Cleaned unused boilerplate Vite icon. |
| `frontend/src/assets/vite.svg` | Deleted | Cleaned unused boilerplate Vite icon. |
