# Launch Script for Notice2Action AI (PS02)
# Windows PowerShell compatible
# Launches the FastAPI Backend and React 19 Frontend

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python virtual environment not found at $PythonExe." -ForegroundColor Red
    Write-Host "Please run .\scripts\setup.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Launching Notice2Action AI Full-Stack Application (PS02)" -ForegroundColor Cyan
Write-Host " React Frontend:  http://127.0.0.1:5173" -ForegroundColor Green
Write-Host " FastAPI Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host " API Docs:        http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Start FastAPI backend in background job
Write-Host "Starting FastAPI backend server on port 8000..." -ForegroundColor Cyan
$BackendJob = Start-Job -ScriptBlock {
    param($root, $py)
    Set-Location $root
    & $py -m uvicorn notice2action.api.server:app --host 127.0.0.1 --port 8000
} -ArgumentList $ProjectRoot, $PythonExe

# Start Vite frontend
Write-Host "Starting Vite React development server on port 5173..." -ForegroundColor Cyan
Set-Location (Join-Path $ProjectRoot "frontend")
try {
    npm run dev -- --host 127.0.0.1 --port 5173
} finally {
    Stop-Job $BackendJob -ErrorAction SilentlyContinue
    Remove-Job $BackendJob -ErrorAction SilentlyContinue
}
