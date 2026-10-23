# Setup Script for SuchnaSetu AI (PS02)
# Windows PowerShell compatible

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " SuchnaSetu AI — Local Environment Setup" -ForegroundColor Cyan
Write-Host " Hacktoberfest 2026 HackDay@Meerut (PS02)" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# 1. Check Python installation
Write-Host "[1/4] Checking Python runtime..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[ERROR] Python was not found in PATH. Please install Python 3.11 or higher." -ForegroundColor Red
    exit 1
}
Write-Host "Found Python: $($py.Source)" -ForegroundColor Green

# 2. Virtual Environment
Write-Host "[2/4] Setting up project-local virtual environment (.venv)..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    $uv = Get-Command uv -ErrorAction SilentlyContinue
    if ($uv) {
        Write-Host "Using uv to create virtual environment..." -ForegroundColor Cyan
        uv venv --python 3.11 .venv
    } else {
        Write-Host "Using standard python venv module..." -ForegroundColor Cyan
        python -m venv .venv
    }
} else {
    Write-Host ".venv already exists. Skipping recreation." -ForegroundColor Green
}

# 3. Installing dependencies
Write-Host "[3/4] Installing required dependencies..." -ForegroundColor Yellow
$PythonVenv = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$uv = Get-Command uv -ErrorAction SilentlyContinue
if ($uv) {
    uv pip install --python $PythonVenv -r requirements.txt
    uv pip install --python $PythonVenv -e .
} else {
    & $PythonVenv -m pip install --upgrade pip
    & $PythonVenv -m pip install -r requirements.txt
    & $PythonVenv -m pip install -e .
}

# 4. Copy .env if not exists
Write-Host "[4/4] Checking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host ".env already present." -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " Setup complete! Next steps:" -ForegroundColor Green
Write-Host " 1. Run Preflight:   .\scripts\preflight.ps1" -ForegroundColor Cyan
Write-Host " 2. Run Tests:       .\scripts\test.ps1" -ForegroundColor Cyan
Write-Host " 3. Launch App:      .\scripts\run.ps1" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
