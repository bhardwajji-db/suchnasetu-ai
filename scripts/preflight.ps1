# Preflight Diagnostic Script for Notice2Action AI (PS02)
# Windows PowerShell compatible

$ErrorActionPreference = "Continue"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Notice2Action AI — Preflight Diagnostic Check (PS02)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Check Python in .venv
$PythonVenv = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
if (Test-Path $PythonVenv) {
    Write-Host "[OK] Local Virtual Environment found: $PythonVenv" -ForegroundColor Green
    & $PythonVenv -c "
import sys; sys.path.insert(0, 'src')
from notice2action.config import run_preflight_diagnostics
report = run_preflight_diagnostics()
print('\nDiagnostic Results:')
for item in report.items:
    status_color = 'OK' if item.status == 'ok' else ('WARN' if item.status == 'warning' else 'FAIL')
    print(f'  [{status_color}] {item.name}: {item.details}')
    if item.remedy:
        print(f'         Remedy: {item.remedy}')
print(f'\nOverall System Status: {report.overall_status.upper()}')
"
} else {
    Write-Host "[WARN] .venv not found. Running system Python check..." -ForegroundColor Yellow
    python -c "import sys; print(f'System Python: {sys.version}')"
    Write-Host "Run .\scripts\setup.ps1 to create the local virtual environment." -ForegroundColor Yellow
}
