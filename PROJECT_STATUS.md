# SochnaSetu AI — Project Status & Operational Summary

**Last Updated:** November 16, 2026  
**Status:** 🟢 Operational & Production-Ready  
**Architecture:** Single-Entry Local Deployment with Cloudflare Tunnel Edge  

---

## 1. System Overview

SochnaSetu AI is an offline-first, privacy-preserving legal and administrative document intelligence system designed for academic notices, government circulars, and scholarship announcements.

### Key Capabilities
- **100% Local OCR & AI Pipeline:** Tesseract OCR v5.4.0 with automated multi-script language detection (English/Hindi), 4-angle rotation correction (0°, 90°, 180°, 270°), and Local Ollama (`gemma4:latest`).
- **Human Review System:** Bounding-box visualization, low-confidence word flagging, inline editing, and atomic persistence in SQLite (`data/suchnasetu.db`).
- **Explainable Eligibility Engine:** Deterministic rule extraction, age cutoff evaluations, and statutory quota relaxations.
- **Revision Ledger:** Cross-notice delta comparisons, corrigendum matching, and personal impact change tracking.
- **Single-Entry Launcher:** `LOCAL_DEPLOY.bat` managing full orchestration and Cloudflare tunnel bridging.

---

## 2. Deployment Architecture & Single-Entry Launcher

### Launcher: `LOCAL_DEPLOY.bat`
A root double-clickable batch script orchestrating the full application stack via `scripts/deploy_manager.py`:

```
[LOCAL_DEPLOY.bat]
       │
       ▼
[scripts/deploy_manager.py]
  ├── 1. Preflight Verification (Python 3.11, Node.js, .env, cloudflared)
  ├── 2. SQLite Database Integrity Check (DatabaseManager)
  ├── 3. Local Ollama Probing (port 11434, gemma4:latest)
  ├── 4. FastAPI Backend Startup (uvicorn app.main:app, port 8000)
  ├── 5. Vite Frontend Startup (npm run dev, port 5173, allowedHosts: true)
  └── 6. Cloudflare Tunnel Bridge (HTTP/2 edge tunnel to port 8000)
```

### Verified Service Endpoints
- **Local Frontend:** [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **Local Backend API:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Local Ollama LLM:** [http://127.0.0.1:11434](http://127.0.0.1:11434)
- **Public Cloudflare Tunnel:** `https://*.trycloudflare.com` (dynamically synced to `.env` and `logs/active_tunnel_url.txt`)

---

## 3. Codebase Simplification & Cleanup

Obsolete, redundant, and conflicting files were safely purged without affecting core business logic, user uploads, or database records:

| File / Folder Removed | Reason for Removal | Status |
|---|---|---|
| `run_app.bat` | Redundant launcher superseded by `LOCAL_DEPLOY.bat` | Deleted |
| `start_all.bat` | Outdated multi-process launcher superseded by `LOCAL_DEPLOY.bat` | Deleted |
| `start_tunnel.bat` | Fragmented tunnel-only script merged into `deploy_manager.py` | Deleted |
| `start_production.bat` | Contained hardcoded dead Cloudflare URLs | Deleted |
| `scripts/start_production.ps1` | Redundant PowerShell script with hardcoded hostnames | Deleted |
| `scripts/update_inventory_test.py` | One-off scratch test script | Deleted |
| `scripts/update_master_test.py` | One-off scratch test script | Deleted |
| `scripts/audit_buttons.py` | Temporary diagnostic script | Deleted |
| `.quarantine/` | 90+ MB legacy backup archive | Purged |

Full cleanup documentation is preserved in [CLEANUP_REPORT.md](file:///c:/Users/Avinash/OneDrive/Desktop/AI-Projects/Hacktober%20fest/ps2/CLEANUP_REPORT.md).

---

## 4. Test Verification & Quality Assurance

### Backend Test Suite
- **Executed:** `pytest` / `pytest tests/test_ocr_intelligence_and_human_review.py tests/test_orientation_recovery.py`
- **Result:** **37 passed, 1 skipped** (Overall) / **29 passed, 1 skipped** (OCR & Orientation suite)
- **Coverage Areas:**
  - Automatic language detection (English, Hindi, mixed Devanagari/Latin scripts)
  - 4-way orientation recovery (0°, 90°, 180°, 270°) with bounding box re-projection
  - Human Review CRUD and canonical notice text synchronization
  - Fast-path text extraction for digital PDFs with image scan fallbacks

### Frontend Test Suite
- **Executed:** `npm test -- --run` (Vitest)
- **Result:** **26 test files passed, 97 tests passed (100% success)**
- **Build Verification:** `npm run build` compiled cleanly into `frontend/dist` in 770ms.

---

## 5. Operations & Execution

To launch the entire platform:
1. Double-click `LOCAL_DEPLOY.bat` or run:
   ```cmd
   LOCAL_DEPLOY.bat
   ```
2. The orchestrator will check dependencies, initialize the database, boot services, establish the Cloudflare tunnel, and print the active local and public URLs.
3. Press `Ctrl+C` to gracefully terminate all spawned processes.
