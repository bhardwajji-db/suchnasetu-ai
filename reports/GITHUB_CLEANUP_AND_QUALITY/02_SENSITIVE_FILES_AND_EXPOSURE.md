# 02. SENSITIVE FILES & EXPOSURE AUDIT — SOCHNASETU AI

This report catalogs all runtime, environment, and user data files, classifying their tracking state and verifying that sensitive material is not published to GitHub.

---

## 1. Classification of Tracked and Ignored Assets

| File / Pattern | Intended Purpose | Tracking State | Git Status | Exposure Risk | Verification Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `.env` | Local development secrets & keys | Untracked | Ignored (`.gitignore`) | None | **PASS (Protected)** |
| `.env.example` | Generic configuration template | Tracked | Tracked | None (Placeholders only) | **PASS (Safe)** |
| `.env.production.example`| Production deployment template | Tracked | Tracked | None (Placeholders only) | **PASS (Safe)** |
| `data/suchnasetu.db` | Local SQLite database | Untracked | Ignored (`data/*.db`)| None | **PASS (Protected)** |
| `data/uploads/*` | Temporary uploaded files | Untracked | Ignored (`data/uploads/*`)| None | **PASS (Protected)** |
| `.sessions/*` | Per-user session caches | Untracked | Ignored (`.sessions/`)| None | **PASS (Protected)** |
| `*.log` | Runtime log outputs | Untracked | Ignored (`*.log`)| None | **PASS (Protected)** |
| `frontend/node_modules/` | Node dependencies | Untracked | Ignored | None | **PASS (Protected)** |
| `frontend/dist/` | Compiled production bundle | Untracked | Ignored | None | **PASS (Protected)** |
| `.venv/` | Python virtual environment | Untracked | Ignored | None | **PASS (Protected)** |

---

## 2. Personal Machine Path Remediation

During the audit, 45 occurrences of developer-specific absolute paths (e.g. `C:\Users\Avinash\...` and `file:///C:/Users/Avinash/...`) were detected in documentation and report files.

- **Status:** **REMEDIATED.**
- **Action:** Executed `scripts/sanitize_machine_paths.py` replacing all machine-specific paths with clean relative links (`./`) or generic placeholders (`<project-root>`, `%LOCALAPPDATA%`).
- **Post-Remediation Scan:** Re-scan via `scripts/scan_secrets_and_paths.py` confirmed **0 personal machine absolute paths remain in the repository**.
