# SochnaSetu AI — Enterprise Production Deployment Guide

**Application:** SochnaSetu AI — Notice-to-Action Accessibility Assistant (PS02)  
**Target Environments:** Docker & Docker Compose, Bare-Metal Linux (Ubuntu/Debian), Cloud PaaS (Render/Railway/Fly.io), and Local Production LAN.  
**Security Standard:** 100% Free & Local-First, Zero Third-Party Cloud Dependencies, Air-Gapped Privacy Guaranteed.

---

## 1. Architecture Overview

```mermaid
flowchart TD
    subgraph Client Layer
        Browser[Desktop / Laptop Browser]
        Mobile[Android / iOS Phone (LAN)]
        Tablet[Tablet (Portrait / Landscape)]
    end

    subgraph Reverse Proxy / Ingress
        NGINX[Nginx / Caddy / Cloud Ingress (Port 80/443)]
    end

    subgraph SochnaSetu Unified Application Service (Port 8000)
        SPA[React 19 + Vite Compiled SPA (Root /)]
        FASTAPI[FastAPI ASGI Application (/api/*)]
        SECURITY[Security & Anti-Injection Sanitizer]
        TRUST[Evidence-First Trust Engine]
        ELIGIBILITY[Explainable Eligibility Matcher]
        REVISION[Revision Ledger & Corrigendum Tracker]
        IMPACT[Personal Impact Change Tracker]
        STORAGE[SQLite Persistent Store (data/suchnasetu.db)]
    end

    subgraph Local Inference & OCR Engines
        TESSERACT[Tesseract 5.4 OCR (eng, hin, osd)]
        OLLAMA[Local Ollama Daemon (Port 11434)]
        GEMMA[Gemma 4:latest 100% Offline Model]
    end

    Browser -->|HTTP/HTTPS| NGINX
    Mobile -->|HTTP/HTTPS| NGINX
    Tablet -->|HTTP/HTTPS| NGINX

    NGINX -->|Reverse Proxy| FASTAPI
    FASTAPI -->|Serves Static UI| SPA
    FASTAPI --> SECURITY
    FASTAPI --> TRUST
    FASTAPI --> ELIGIBILITY
    FASTAPI --> REVISION
    FASTAPI --> IMPACT
    FASTAPI --> STORAGE
    FASTAPI -->|Subprocess| TESSERACT
    FASTAPI -->|Local HTTP 11434| OLLAMA
    OLLAMA --> GEMMA
```

---

## 2. Deployment Mode 1: Docker & Docker Compose (Recommended)

Docker Compose provides a complete, one-command deployment orchestrating both the application container and the local Ollama inference service with persistent volume storage.

### Prerequisites
- Docker Engine version 24.0+
- Docker Compose v2.0+
- 8GB RAM minimum (16GB recommended for full Gemma 4 inference)

### Directory Configuration
Ensure your repository root contains:
- `Dockerfile` (Multi-stage build)
- `docker-compose.yml`
- `.dockerignore`

### Deployment Steps
```bash
# 1. Clone repository
git clone https://github.com/bhardwajji-db/suchnasetu-ai.git
cd suchnasetu-ai

# 2. Build and launch all containers in detached mode
docker compose up --build -d

# 3. Pull the local Gemma 4 model inside the Ollama container (first-time only)
docker exec -it sochnasetu-ollama ollama pull gemma4:latest

# 4. Verify service health
curl -f http://localhost:8000/api/health
```

### Access Points
- **Web Application & API:** `http://localhost:8000`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **Local Ollama Daemon:** `http://localhost:11434`

### Optional: GPU Acceleration (NVIDIA CUDA)
To enable GPU acceleration for sub-second inference speeds in Docker:
1. Install NVIDIA Container Toolkit (`nvidia-container-toolkit`).
2. Uncomment the `deploy.resources.reservations.devices` block in `docker-compose.yml`:
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```

---

## 3. Deployment Mode 2: Bare-Metal Linux Server (Ubuntu 22.04 / 24.04 LTS)

For dedicated on-premise servers or virtual private servers (VPS):

### Step 1: System Packages Installation
```bash
sudo apt update && sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-hin \
    tesseract-ocr-osd \
    poppler-utils \
    curl \
    git \
    nginx
```

### Step 2: Install and Start Ollama
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the Gemma 4 model
ollama pull gemma4:latest

# Verify Ollama service is active
systemctl status ollama
```

### Step 3: Clone Codebase and Setup Virtual Environment
```bash
git clone https://github.com/bhardwajji-db/suchnasetu-ai.git /opt/suchnasetu-ai
cd /opt/suchnasetu-ai

# Create virtual environment and install dependencies
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Compile frontend static bundle
cd frontend
npm ci && npm run build
cd ..
```

### Step 4: Configure Systemd Service
Create `/etc/systemd/system/suchnasetu.service`:
```ini
[Unit]
Description=SochnaSetu AI Production ASGI Server
After=network.target ollama.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/suchnasetu-ai
Environment="PYTHONPATH=/opt/suchnasetu-ai/src"
Environment="APP_ENV=production"
Environment="HOST=127.0.0.1"
Environment="PORT=8000"
Environment="OLLAMA_BASE_URL=http://127.0.0.1:11434"
Environment="OLLAMA_MODEL=gemma4:latest"
ExecStart=/opt/suchnasetu-ai/.venv/bin/python -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo chown -R www-data:www-data /opt/suchnasetu-ai/data
sudo systemctl daemon-reload
sudo systemctl enable --now suchnasetu
```

### Step 5: Nginx Reverse Proxy & SSL Configuration
Create `/etc/nginx/sites-available/suchnasetu`:
```nginx
server {
    listen 80;
    server_name notices.example.gov.in; # Replace with your domain or IP

    client_max_body_size 25M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the site and reload Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/suchnasetu /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## 4. Deployment Mode 3: Cloud PaaS (Render, Railway, Fly.io)

SochnaSetu AI includes a production `Procfile` and `Dockerfile` for single-click PaaS container deployments:

### Configuration on Render / Railway
1. **Build Type:** Dockerfile (Multi-stage)
2. **Environment Variables:**
   - `APP_ENV=production`
   - `PORT=8000`
   - `OLLAMA_BASE_URL`: URL to your Ollama container instance, or external private endpoint
   - `MAX_UPLOAD_SIZE_MB=15`
3. **Health Check Path:** `/api/health`
4. **Persistent Disk (Optional):** Mount disk to `/app/data` to persist user-submitted notices and SQLite history across redeployments.

---

## 5. Deployment Mode 4: Windows Local Production & Wi-Fi LAN

For local government offices, university departments, or competition evaluation laptops:

1. Double-click `start_production.bat`.
2. The script:
   - Verifies the Python virtual environment.
   - Compiles the React 19 production bundle into `frontend/dist`.
   - Starts the Ollama daemon and checks model readiness.
   - Launches the unified server on `http://0.0.0.0:8000`.
   - Detects the local Wi-Fi IP (e.g. `192.168.29.182`) and opens the default browser.
3. Any mobile phone, tablet, or secondary PC on the same Wi-Fi can navigate to:
   ```
   http://<YOUR_WIFI_IP>:8000
   ```
