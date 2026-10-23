# Preflight Diagnostic Script for SuchnaSetu AI (PS02)
# Windows PowerShell compatible

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " SuchnaSetu AI -- Preflight Diagnostic Check (PS02)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PythonVenv = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PreflightScript = Join-Path $ProjectRoot "scripts\preflight.py"

if (Test-Path $PythonVenv) {
    Write-Host "[OK] Local Virtual Environment found: $PythonVenv" -ForegroundColor Green
    & $PythonVenv $PreflightScript
} else {
    Write-Host "[WARN] .venv not found. Running system Python check..." -ForegroundColor Yellow
    python $PreflightScript
    Write-Host "Run .\scripts\setup.ps1 to create the local virtual environment." -ForegroundColor Yellow
}
