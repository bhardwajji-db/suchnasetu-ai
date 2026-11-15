# SochnaSetu AI — Local Deployment & Operations Guide

This guide details the single-entry local deployment system for SochnaSetu AI, including service orchestration, port assignments, Cloudflare Tunnel integration, and operational troubleshooting.

---

## 1. Quick Start: The Single Entry Point

To launch the complete SochnaSetu AI application with all local services, database connectivity, and an external Cloudflare Tunnel, run the single master launcher in the project root:

```cmd
LOCAL_DEPLOY.bat
```

You can double-click **`LOCAL_DEPLOY.bat`** directly from Windows File Explorer or execute it from a Command Prompt / PowerShell terminal.

You do **not** need to open multiple terminal tabs or run separate commands for the backend, frontend, database, and tunnel.

---

## 2. Startup Orchestration Sequence

When executed, `LOCAL_DEPLOY.bat` triggers `scripts/deploy_manager.py`, executing the following deterministic sequence:

1. **Preflight Environment Verification:**
   - Verifies the Python 3.11 virtual environment at `.venv\Scripts\python.exe`.
   - Verifies Node.js (v18+) and npm in the system PATH.
   - Verifies `frontend\node_modules` (installs via `npm install` if missing).
   - Verifies configuration file `.env` (copies from `.env.example` if missing).
   - Locates `cloudflared` executable on the system.
2. **Database Verification:**
   - Verifies the embedded SQLite database (`data/suchnasetu.db`) and table schemas (`documents`, `analyses`, `checklist_items`).
3. **AI Service Detection (Ollama):**
   - Probes `http://127.0.0.1:11434/api/tags` to see if Ollama is running.
   - If offline, attempts to start `ollama serve` in the background (tracking ownership).
   - Probes for the configured model (`gemma4:latest`).
   - If Ollama or the model is unavailable, gracefully configures the application in deterministic regex fallback mode without blocking deployment.
4. **FastAPI Backend Initialization:**
   - Checks port `8000`. If an existing healthy instance is running, reuses it.
   - Otherwise, starts Uvicorn ASGI server: `python -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000`.
   - Polls `http://127.0.0.1:8000/health` up to 25 seconds until HTTP 200 OK is confirmed.
5. **React 19 Frontend Initialization:**
   - Checks port `5173`. If an existing responsive instance is running, reuses it.
   - Otherwise, starts Vite development server: `npm run dev -- --host 127.0.0.1 --port 5173`.
   - Polls `http://127.0.0.1:5173` up to 25 seconds until HTTP 200 OK is confirmed.
   - The Vite dev server automatically proxies all `/api` requests to `http://127.0.0.1:8000`.
6. **Cloudflare Tunnel Establishment:**
   - Cleans up any stale or zombie `cloudflared` instances.
   - Launches `cloudflared` with HTTP/2 protocol over TLS to eliminate connection drops and Error 1033.
   - Scans stream output for the dynamic public URL (`https://*.trycloudflare.com`).
   - Automatically synchronizes `AUTH_PUBLIC_APP_URL`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` in `.env`.
   - Writes the live URL to `logs/active_tunnel_url.txt`.
7. **Terminal Summary Display:**
   - Prints the consolidated service health matrix and all local/public links.

---

## 3. Service URLs and Endpoints

| Service | Address | Description |
|---|---|---|
| **Local Application (Frontend)** | `http://localhost:5173` | Main interactive React 19 single-page application with hot module reloading. |
| **Backend REST API** | `http://127.0.0.1:8000` | FastAPI ASGI application serving all document intelligence routes. |
| **Interactive API Documentation** | `http://127.0.0.1:8000/docs` | Swagger UI documentation with live endpoint testing. |
| **Alternative OpenAPI Docs** | `http://127.0.0.1:8000/redoc` | ReDoc API specification documentation. |
| **Public Application (Cloudflare)** | `https://<dynamic-subdomain>.trycloudflare.com` | Globally accessible public URL for mobile, external, and jury evaluation. |
| **Ollama Local AI API** | `http://127.0.0.1:11434` | Local model inference daemon (Gemma 4). |

---

## 4. Cloudflare Tunnel Behavior & Offline Handling

- **Protocol:** Uses HTTP/2 over TLS (`--protocol http2 --edge-ip-version auto`), avoiding UDP/QUIC drops.
- **Dynamic Quick Tunnels:** By default, cloudflared generates an ephemeral `*.trycloudflare.com` URL without requiring an account.
- **Permanent Named Tunnels:** If you have a Cloudflare account with a named tunnel, set `CLOUDFLARE_TUNNEL_TOKEN=<your_token>` in `.env`. The launcher will automatically use your permanent domain instead of an ephemeral one.
- **Offline / No Internet Behavior:** If internet connectivity is down or `cloudflared` cannot connect, the launcher prints:
  ```text
  [WARN] Cloudflare Tunnel is unavailable
  PUBLIC APPLICATION:
  Public access unavailable (Cloudflare Tunnel disconnected)
  ```
  Local services (`http://localhost:5173` and `http://127.0.0.1:8000`) continue to operate normally with 100% functionality.

---

## 5. Log Files and Diagnostic Trails

All application logs are recorded under `logs/` for monitoring and troubleshooting:

| Log File | Path | Description |
|---|---|---|
| **Backend Log** | `logs/backend.log` | FastAPI startup logs, Uvicorn request traces, and unhandled Python exceptions. |
| **Frontend Log** | `logs/frontend.log` | Vite dev server compilation output and proxy messages. |
| **Cloudflare Log** | `logs/cloudflared.log` | Cloudflare tunnel edge connection logs, TLS handshakes, and route mapping. |
| **Active Tunnel URL** | `logs/active_tunnel_url.txt` | Single-line text file containing the current active public URL. |
| **Process PID File** | `.deploy_pids.json` | JSON file tracking active PIDs spawned by the launcher. |

---

## 6. Stopping Services (Graceful Shutdown)

Press **`Ctrl+C`** in the terminal where `LOCAL_DEPLOY.bat` is running.

The shutdown handler will:
1. Terminate the active Cloudflare Tunnel process.
2. Terminate the Vite frontend process.
3. Terminate the FastAPI backend process.
4. If Ollama was pre-existing before launch, it is **left running**. If Ollama was started by the launcher, it is gracefully stopped.
5. Clean up `.deploy_pids.json`.

---

## 7. Troubleshooting & FAQ

### Port 8000 or 5173 is already in use
If an old backend or Vite process was left running from a previous crash:
```powershell
# Check what process is using port 8000
Get-NetTCPConnection -LocalPort 8000 -State Listen
# Terminate stray uvicorn or node processes
Get-Process python, node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "uvicorn|vite" } | Stop-Process -Force
```

### Missing Python Virtual Environment
If `.venv` is missing:
```powershell
.\scripts\setup.ps1
```

### Missing Frontend Dependencies
If `frontend\node_modules` is corrupted or missing:
```cmd
cd frontend
npm install
```

### Cloudflared Not Found
If Cloudflare tunnel shows as unavailable:
```powershell
winget install Cloudflare.cloudflared
```
Or download the Windows 64-bit binary from Cloudflare and place it into `C:\Program Files (x86)\cloudflared\cloudflared.exe`.
