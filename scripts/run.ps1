# Launch Script for Notice2Action AI (PS02)
# Windows PowerShell compatible

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$StreamlitExe = Join-Path $ProjectRoot ".venv\Scripts\streamlit.exe"
if (-not (Test-Path $StreamlitExe)) {
    Write-Host "[ERROR] Streamlit executable not found in .venv." -ForegroundColor Red
    Write-Host "Please run .\scripts\setup.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Launching Notice2Action AI (PS02)" -ForegroundColor Cyan
Write-Host " Local Web App: http://localhost:8501" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

& $StreamlitExe run app.py --server.headless false
