# SuchnaSetu AI — Troubleshooting & Operations Guide

This guide covers common setup, runtime, and environment issues on Windows.

---

## 1. Quick Diagnostics

Run the preflight diagnostic command in Windows PowerShell:
```powershell
.\scripts\preflight.ps1
```
This inspects:
- Python virtual environment (`.venv`)
- Tesseract OCR binary and language packs
- Ollama server connectivity (http://127.0.0.1:11434)
- Installed models (`gemma4:latest`)

---

## 2. Common Issues and Remedies

### A. Ollama Server Connection Error
**Symptoms:**
- Preflight reports `Cannot connect to Ollama at http://127.0.0.1:11434`.
- App displays `🔴 System Error (Ollama/Model Missing)`.

**Remedy:**
1. Open a new PowerShell terminal and run:
   ```powershell
   ollama serve
   ```
2. Verify Ollama responds:
   ```powershell
   ollama list
   ```
3. Refresh the Notice2Action app in your browser.

---

### B. Target Model `gemma4:latest` Not Found
**Symptoms:**
- Ollama is running, but preflight reports model missing.

**Remedy:**
1. Check downloaded models:
   ```powershell
   ollama list
   ```
2. If `gemma4:latest` is absent, pull or verify tag:
   ```powershell
   ollama run gemma4:latest
   ```
3. Alternatively, edit `.env` to specify another installed model tag if testing:
   ```env
   OLLAMA_MODEL=gemma4:latest
   ```

---

### C. Tesseract OCR Not Found
**Symptoms:**
- Preflight reports `Tesseract binary not found in standard paths`.
- Image OCR fails with executable error.

**Remedy:**
1. Install Tesseract OCR for Windows from:
   https://github.com/UB-Mannheim/tesseract/wiki
2. The installer installs to `C:\Program Files\Tesseract-OCR\tesseract.exe`.
3. If installed in a non-standard path, set `TESSERACT_CMD` in `.env`:
   ```env
   TESSERACT_CMD=D:\CustomPath\Tesseract-OCR\tesseract.exe
   ```

---

### D. PowerShell Execution Policy Restriction
**Symptoms:**
- Running `.\scripts\setup.ps1` gives error: `File cannot be loaded because running scripts is disabled on this system`.

**Remedy:**
Run the following in PowerShell:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
Then rerun the script.

---

### E. Port 8501 Already in Use
**Symptoms:**
- Streamlit fails to bind to port 8501.

**Remedy:**
Run on an alternate port:
```powershell
.\.venv\Scripts\streamlit.exe run app.py --server.port 8502
```
