# Single-command HackDay Readiness Verification Runner for SuchnaSetu AI
# Windows PowerShell compatible

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python virtual environment not found at $PythonExe" -ForegroundColor Red
    exit 1
}

& $PythonExe (Join-Path $ProjectRoot "scripts\verify_hackday_readiness.py")
