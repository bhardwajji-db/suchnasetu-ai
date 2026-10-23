# SuchnaSetu AI — Complete Setup & Run Guide (Windows)

Welcome to **SuchnaSetu AI (Notice-to-Action Accessibility Assistant)**!  
This guide will walk you through setting up and running the entire project on a Windows laptop from scratch.

---

## 📋 Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Cloning the Repository](#2-cloning-the-repository)
3. [Creating & Activating Python Virtual Environment](#3-creating--activating-python-virtual-environment)
4. [Installing Backend Dependencies](#4-installing-backend-dependencies)
5. [Installing Frontend Dependencies](#5-installing-frontend-dependencies)
6. [Configuring Environment Variables](#6-configuring-environment-variables)
7. [Installing & Verifying Tesseract OCR & Ollama](#7-installing--verifying-tesseract-ocr--ollama)
8. [Starting Backend & Frontend Services](#8-starting-backend--frontend-services)
9. [Running Automated Tests](#9-running-automated-tests)
10. [Troubleshooting Common Issues](#10-troubleshooting-common-issues)

---

## 1. Prerequisites

Before starting, ensure your system has the following installed:

| Requirement | Supported Version | Notes / Download Link |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 or 11 (64-bit) | PowerShell 5.1 or PowerShell 7 |
| **Python** | Python 3.11.x | [python.org/downloads](https://www.python.org/downloads/) *(Check "Add python.exe to PATH" during install)* |
| **Node.js & npm** | Node.js 18+ LTS or 20+ LTS | [nodejs.org](https://nodejs.org/) *(Includes npm)* |
| **Git** | Git for Windows (2.40+) | [git-scm.com](https://git-scm.com/) |
| **Tesseract OCR** | v5.3+ (v5.4 recommended) | [UB-Mannheim Tesseract Installer](https://github.com/UB-Mannheim/tesseract/wiki) |
| **Ollama** | Latest Windows Release | [ollama.com/download](https://ollama.com/download) *(For 100% offline Gemma 4)* |

---

## 2. Cloning the Repository

Open **PowerShell** and clone the repository to your preferred projects directory (e.g., `C:\Projects`):

```powershell
# Create your development folder if not already present
mkdir C:\Projects -ErrorAction SilentlyContinue
cd C:\Projects

# Clone the repository
git clone https://github.com/bhardwajji-db/suchnasetu-ai.git
cd suchnasetu-ai
```

---

## 3. Creating & Activating Python Virtual Environment

Keep your system Python clean by creating a dedicated virtual environment (`.venv`) inside the project root:

```powershell
# Create the virtual environment using Python 3.11
python -m venv .venv

# If PowerShell script execution is restricted on your system, enable it for this process:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

*(You will see `(.venv)` in your PowerShell prompt indicating the virtual environment is active).*

---

## 4. Installing Backend Dependencies

With `(.venv)` active, install the required packages and register the internal `notice2action` package in editable mode:

```powershell
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install the notice2action package in editable mode
pip install -e .
```

---

## 5. Installing Frontend Dependencies

The web interface is built with React 19, TypeScript, and Vite:

```powershell
# Navigate into the frontend folder and install npm packages
cd frontend
npm install

# Return to the project root
cd ..
```

---

## 6. Configuring Environment Variables

SuchnaSetu AI includes a safe `.env.example` template. Copy it to create your local `.env`:

```powershell
Copy-Item .env.example .env
```

### Local vs. Cloud Provider Modes:
- **Local Air-Gapped Mode (Default):**  
  No API keys required! By default, `LLM_PROVIDER=ollama` will use your local Gemma 4 model via Ollama. It runs 100% offline with zero cloud data transmission.
- **Optional Cloud Provider Mode:**  
  If you prefer using cloud models, open `.env` in a text editor and enter your key:
  - For Google Gemini: Set `LLM_PROVIDER=gemini` and provide `GEMINI_API_KEY=your_key_here`.
  - For OpenRouter: Set `LLM_PROVIDER=openrouter` and provide `OPENROUTER_API_KEY=your_key_here`.
  - For Hugging Face: Set `LLM_PROVIDER=huggingface` and provide `HUGGINGFACE_API_KEY=your_token_here`.

> [!NOTE]
> Your `.env` file is strictly ignored by Git (`.gitignore`). Never commit API keys or credentials.

---

## 7. Installing & Verifying Tesseract OCR & Ollama

### A. Tesseract OCR (For Document & Image Reading)
1. Download and run the Windows 64-bit installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install to the default location: `C:\Program Files\Tesseract-OCR\`.
3. In the installer component selection, ensure **"Additional language data (download)"** -> **"Hindi"** is selected, or copy `hin.traineddata` from `assets/tessdata/` into `C:\Program Files\Tesseract-OCR\tessdata\`.
4. Verify installation in PowerShell:
   ```powershell
   & "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
   ```

### B. Ollama & Gemma 4 (For On-Device Intelligence)
1. Install Ollama from [ollama.com/download](https://ollama.com/download).
2. Pull the Gemma 4 model (or your preferred quantized variant):
   ```powershell
   ollama pull gemma4:latest
   ```
3. Start the Ollama server in a background or separate terminal:
   ```powershell
   ollama serve
   ```

### C. Run Preflight Diagnostics
The project includes a built-in preflight utility that checks Python, Tesseract, PDF processing, and Ollama:
```powershell
.\scripts\preflight.ps1
```
All essential checks should display **`[OK]`**.

---

## 8. Starting Backend & Frontend Services

### Option A: One-Click Launcher (Recommended for Windows)
Double-click `run_app.bat` or execute in PowerShell:
```powershell
.\run_app.bat
```
This automatically launches:
1. FastAPI Backend at **`http://127.0.0.1:8000`** (API Docs at `http://127.0.0.1:8000/docs`).
2. Vite React Frontend at **`http://127.0.0.1:5173`**.
3. Opens your default web browser to the application dashboard.

---

### Option B: PowerShell Dual-Service Script
```powershell
.\scripts\run.ps1
```

---

### Option C: Manual Launch (Two Terminals)

**Terminal 1 — Backend:**
```powershell
cd C:\Projects\suchnasetu-ai
.\.venv\Scripts\Activate.ps1
python -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```powershell
cd C:\Projects\suchnasetu-ai\frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Open **`http://127.0.0.1:5173`** in your browser.

---

## 9. Running Automated Tests

To ensure everything is working correctly on your machine:

```powershell
# 1. Run all tests via automated PowerShell runner:
.\scripts\test.ps1

# 2. Or run backend pytest suite directly:
.\.venv\Scripts\pytest.exe -m "not live" --tb=short

# 3. Run frontend Vitest component tests:
npm --prefix frontend run test -- --run

# 4. Check frontend TypeScript compilation & production build:
npm --prefix frontend run build
```

---

## 10. Troubleshooting Common Issues

### Issue 1: `Activate.ps1 cannot be loaded because running scripts is disabled`
- **Cause:** Windows PowerShell execution policy is restricted by default.
- **Fix:** In PowerShell, run:
  ```powershell
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
  ```
  Then re-run `.\.venv\Scripts\Activate.ps1`.

### Issue 2: `tesseract is not installed or it's not in your PATH`
- **Cause:** Tesseract was installed in a non-standard folder or not added to PATH.
- **Fix:** Open `.env` and verify the `TESSERACT_CMD` path points directly to your executable:
  ```ini
  TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
  ```

### Issue 3: `Ollama Server: Cannot connect to http://127.0.0.1:11434`
- **Cause:** The Ollama service is not running.
- **Fix:** Open a PowerShell terminal and run:
  ```powershell
  ollama serve
  ```
  Keep the terminal open, or configure Ollama to run on Windows startup.

### Issue 4: Port 8000 or 5173 Already in Use
- **Cause:** Another local development server is bound to the port.
- **Fix:** Check which process is using the port:
  ```powershell
  Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
  ```
  Terminate the conflicting process or change the port in `run_app.bat` / `vite.config.ts`.

### Issue 5: Missing Hindi OCR Support
- **Cause:** Tesseract language data for Hindi (`hin.traineddata`) is missing from Tesseract's `tessdata` directory.
- **Fix:** Copy `assets/tessdata/hin.traineddata` into `C:\Program Files\Tesseract-OCR\tessdata\`.
