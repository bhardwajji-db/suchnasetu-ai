# SochnaSetu AI — Production Deployment & Local Operations Guide

**Application:** SuchnaSetu AI (Notice-to-Action Citizen Accessibility Assistant — PS02)  
**Document Version:** 2.2.0  
**Target Release:** Pre-HackDay Master Delivery & Production Cloud Readiness  
**Supported Deployment Modes:**
1. **Local Demonstration / Evaluation (Default):** 100% Offline, Air-Gapped via Local Ollama + Google Gemma 4 (Zero Cloud API Keys Required).
2. **Cloud-Native Production:** Fully Managed Cloud Deployment via Linux VPS / Docker + Google Gemini 1.5 Flash / OpenRouter (Completely Decoupled from Local Laptop/Ollama).

---

## 1. System Architecture & Dual-Mode Topology

SochnaSetu AI features a decoupled, multi-provider architecture designed to ensure seamless local evaluation while guaranteeing that public internet hosting never depends on or exposes a personal developer laptop.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MODE A: LOCAL AIR-GAPPED                        │
│                   (Evaluations, Hackathons, Offline)                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [Browser] ─────────> [React 19 SPA :5173]                             │
│                            │                                           │
│                            ▼                                           │
│                       [FastAPI :8000]                                  │
│                        ├── SQLite (WAL)                                │
│                        ├── Tesseract OCR                               │
│                        └── Ollama Adapter (127.0.0.1:11434)            │
│                                  │                                     │
│                                  ▼                                     │
│                            [Gemma 4 8B]                                │
│                     (100% Offline & Zero Cost)                         │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│                      MODE B: CLOUD-NATIVE DEPLOYMENT                   │
│                     (Live Public Web Hosting)                          │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  [Public Internet]                                                     │
│        │ HTTPS                                                         │
│        ▼                                                               │
│  [Cloudflare CDN / WAF]                                                │
│   ├── DDoS Protection & Rate Limiting                                  │
│   └── SSL/TLS Termination                                              │
│        │                                                               │
│        ▼                                                               │
│  [Cloud Linux VPS / Container] (Render, Railway, Fly.io, AWS, DO)      │
│   ├── Nginx (Reverse Proxy & Static SPA Host)                          │
│   ├── FastAPI Backend (Uvicorn 127.0.0.1:8000)                         │
│   └── SQLite Persistent Storage Volume (`suchnasetu.db`)               │
│        │                                                               │
│        ▼ (Outbound HTTPS only)                                         │
│  [Google Gemini 1.5 Flash / OpenRouter API]                            │
│                                                                        │
│  * Developer Laptop is completely offline and NOT connected *           │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mode A: Running Locally (Ollama + Gemma 4)

### Prerequisites
- **Operating System:** Windows 10/11, macOS, or Linux.
- **Python:** Version 3.11 or higher.
- **Node.js:** Version 18.0 or higher.
- **Ollama:** Installed from [ollama.com](https://ollama.com).
- **Tesseract OCR:** Installed with English and Hindi language data.
  - Windows: Default path `C:\Program Files\Tesseract-OCR\tesseract.exe`.
  - Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-hin`

### Quick Start (Windows)

1. **Pull the Gemma 4 Model:**
   ```powershell
   ollama pull gemma4:latest
   ```

2. **One-Click Automated Launch:**
   Double-click `run_app.bat` or `start_all.bat` in the project root:
   ```cmd
   .\start_all.bat
   ```
   This script automatically:
   - Verifies the Python virtual environment (`.venv`).
   - Checks if Ollama is running on `127.0.0.1:11434` (starting it minimized if not).
   - Starts the FastAPI backend daemon on `http://127.0.0.1:8000`.
   - Starts the React 19 Vite dev server on `http://127.0.0.1:5173`.
   - Opens the application in your default browser.

3. **Manual Startup Commands (Cross-Platform):**
   ```bash
   # Terminal 1: Start Ollama
   ollama serve

   # Terminal 2: Start FastAPI Backend
   # Activate virtual environment first
   python -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000

   # Terminal 3: Start React 19 Frontend
   cd frontend
   npm install
   npm run dev
   ```

4. **Verify Local Health:**
   - Open: `http://localhost:5173`
   - Backend API Docs: `http://localhost:8000/docs`
   - Health Diagnostic: `http://localhost:8000/api/health`

---

## 3. Mode B: Cloud-Native Public Deployment

To deploy SochnaSetu AI publicly without exposing your personal laptop or local Ollama daemon, use the built-in multi-provider cloud adapter.

### Step 1: Obtain Cloud Provider Credentials
Choose your target provider:
- **Hugging Face Inference Providers (Gemma 4):** Obtain a User Access Token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens). Set `HF_TOKEN`. Target model: `google/gemma-4-26B-A4B`.
- **Google Gemini:** Get an API key at [Google AI Studio](https://aistudio.google.com/). Set `GEMINI_API_KEY`.
- **OpenRouter:** Get an API key at [OpenRouter](https://openrouter.ai/). Set `OPENROUTER_API_KEY`.

### Step 2: Configure Production Environment (`.env`)
Create `.env` on your cloud server (based on `.env.example`):

```ini
# Production Environment Flag
APP_ENV=production

# Server Host & Port
HOST=127.0.0.1
PORT=8000

# Cloud LLM Provider Selection: "huggingface", "gemini", or "openrouter"
AI_PROVIDER=huggingface
HF_TOKEN=your_huggingface_token_here
HF_MODEL_ID=google/gemma-4-26B-A4B
HF_PROVIDER=auto

# Optional Fallback Providers
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-flash
OPENROUTER_API_KEY=
OPENROUTER_MODEL=google/gemma-2-9b-it:free

# Security Secrets (Generate a 64-character random key)
# Command: python -c "import secrets; print(secrets.token_hex(32))"
AUTH_SECRET_KEY=e8d7f3a91b4c6e2f5a0d3b8c7e1f4a9b6c2d5e8f1a4b7c0d3e6f9a2b5c8d1e4f

# HTTPS Cookie Security
AUTH_COOKIE_SECURE=true

# Authorized CORS Origins (Comma-separated exact domains)
CORS_ALLOWED_ORIGINS=https://sochnasetu.yourdomain.com

# Public Web URL for Email Verification & Password Reset Links
AUTH_PUBLIC_APP_URL=https://sochnasetu.yourdomain.com

# Production Email Delivery (Transactional SMTP)
AUTH_EMAIL_BACKEND=smtp
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USERNAME=resend
SMTP_PASSWORD=your_resend_smtp_api_key
SMTP_USE_TLS=true
SMTP_FROM_EMAIL="SochnaSetu AI <notifications@yourdomain.com>"

# Storage Limits
MAX_UPLOAD_SIZE_MB=10
GUEST_RATE_LIMIT_PER_WINDOW=10
```

### Step 3: Build the Frontend Assets
Compile the React 19 TypeScript SPA for production:
```bash
cd frontend
npm ci
npm run build
```
This produces optimized production assets in `frontend/dist/`.

### Step 4: Reverse Proxy Configuration (Nginx Example)
Place Nginx in front of Uvicorn to terminate SSL, serve static files, and forward API requests:

```nginx
server {
    listen 80;
    server_name sochnasetu.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sochnasetu.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/sochnasetu.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sochnasetu.yourdomain.com/privkey.pem;

    # Security Headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options SAMEORIGIN always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    # Client upload limit matching MAX_UPLOAD_SIZE_MB
    client_max_body_size 12M;

    # Serve compiled React 19 SPA
    location / {
        root /var/www/sochnasetu/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to FastAPI
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_read_timeout 120s;
    }
}
```

### Step 5: Process Supervision (Systemd Example)
Create `/etc/systemd/system/sochnasetu.service`:

```ini
[Unit]
Description=SochnaSetu AI FastAPI Backend Service
After=network.target

[Service]
User=sochnasetu
WorkingDirectory=/var/www/sochnasetu
EnvironmentFile=/var/www/sochnasetu/.env
ExecStart=/var/www/sochnasetu/.venv/bin/uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sochnasetu
sudo systemctl start sochnasetu
```

---

## 4. Switching Providers Without Rewriting Code

The entire analysis and question-answering pipeline is decoupled through `BaseLLMClient` and `get_llm_client()`. To change providers, **no code modifications are required** — simply update the environment variable in `.env`:

| Target Provider | Required `.env` Variables | Model Example |
| :--- | :--- | :--- |
| **Local Ollama** (Default) | `LLM_PROVIDER=ollama`<br>`OLLAMA_BASE_URL=http://127.0.0.1:11434` | `gemma4:latest` |
| **Google Gemini** | `LLM_PROVIDER=gemini`<br>`GEMINI_API_KEY=AIzaSy...` | `gemini-1.5-flash`<br>`gemini-2.0-flash` |
| **OpenRouter** | `LLM_PROVIDER=openrouter`<br>`OPENROUTER_API_KEY=sk-or-v1-...` | `google/gemma-2-9b-it:free`<br>`anthropic/claude-3-haiku` |
| **Hugging Face** | `LLM_PROVIDER=huggingface`<br>`HUGGINGFACE_API_KEY=hf_...` | `google/gemma-2-9b-it` |

---

## 5. Operational Maintenance & Database Runbooks

### Database Backup
The SQLite database (`data/suchnasetu.db`) runs with Write-Ahead Logging (WAL mode). To perform a safe hot backup without interrupting live traffic, use SQLite's online backup capability:

```bash
# Hot snapshot using SQLite VACUUM INTO
python -c "
import sqlite3
from pathlib import Path
from datetime import datetime

db_path = Path('data/suchnasetu.db')
backup_dir = Path('data/backups')
backup_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
target = backup_dir / f'suchnasetu_backup_{timestamp}.db'

conn = sqlite3.connect(str(db_path))
conn.execute(f'VACUUM INTO \"{target}\"')
conn.close()
print(f'Backup created at: {target}')
"
```

### Database Integrity Verification
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/suchnasetu.db')
print('Integrity status:', conn.execute('PRAGMA integrity_check').fetchone()[0])
conn.close()
"
```

### Health Check Endpoints
- **System Health:** `GET /api/health` — Returns status of Python runtime, OCR engine, and database connection.
- **Provider Status:** `GET /api/providers` — Returns connection state and configured models for all LLM adapters.
- **Guest Quota Status:** `GET /api/auth/guest-status` — Returns remaining unauthenticated analysis quota for the calling IP.
