# Automated Test Execution Script for Notice2Action AI (PS02)
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
Write-Host " Running Notice2Action AI Backend Test Suites (pytest)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

& $PytestExe tests\test_unit_pipeline.py tests\test_api_endpoints.py tests\test_services_and_six_fields.py tests\test_multi_provider_llm.py tests\test_negative_and_edge_cases.py tests\test_structured_notice_regression.py -v

if ($IncludeFrontend) {
    Write-Host "`n==========================================================" -ForegroundColor Cyan
    Write-Host " Running Frontend Vitest Component Suite" -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Push-Location (Join-Path $ProjectRoot "frontend")
    try {
        npm run test
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
