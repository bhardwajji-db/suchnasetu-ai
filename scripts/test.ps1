# Automated Test Execution Script for SuchnaSetu AI (PS02)
# Windows PowerShell compatible

param (
    [switch]$IncludeLive = $false,
    [switch]$IncludeFrontend = $true
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
Write-Host " Running SuchnaSetu AI Backend Test Suites (pytest)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

& $PytestExe -m "not live" -v

if ($IncludeFrontend) {
    Write-Host "`n==========================================================" -ForegroundColor Cyan
    Write-Host " Running Frontend Vitest Component Suite" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Push-Location (Join-Path $ProjectRoot "frontend")
    try {
        npm run test -- --run
    } finally {
        Pop-Location
    }
}

if ($IncludeLive) {
    Write-Host "`n==========================================================" -ForegroundColor Yellow
    Write-Host " Running Live Gemma 4 & OCR Integration Tests" -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Yellow
    & $PytestExe tests\test_live_gemma4.py -v -s
}
