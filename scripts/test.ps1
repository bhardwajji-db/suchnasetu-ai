# Automated Test Execution Script for Notice2Action AI (PS02)
# Windows PowerShell compatible

param (
    [switch]$IncludeLive = $false
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$PytestExe = Join-Path $ProjectRoot ".venv\Scripts\pytest.exe"
if (-not (Test-Path $PytestExe)) {
    Write-Host "[ERROR] pytest not found in .venv. Run .\scripts\setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Running Notice2Action AI Deterministic Unit Tests" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

& $PytestExe tests\test_unit_pipeline.py -v

if ($IncludeLive) {
    Write-Host "`n==========================================================" -ForegroundColor Yellow
    Write-Host " Running Live Gemma 4 & OCR Integration Tests" -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Yellow
    & $PytestExe tests\test_live_gemma4.py -v -s
}
