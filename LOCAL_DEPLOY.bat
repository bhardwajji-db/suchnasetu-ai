@echo off
setlocal enabledelayedexpansion
title SochnaSetu AI -- Local Deployment
chcp 65001 >nul

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo ========================================================
echo               SOCHNASETU AI
echo         Notice-to-Action Accessibility Suite
echo       Local Deployment & Cloudflare Tunnel Launcher
echo ========================================================
echo.

:: 1. Check Python virtual environment
if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found at .venv\Scripts\python.exe
    echo.
    echo To initialize the environment, please run:
    echo    .\scripts\setup.ps1
    echo or install Python 3.11+ and create a virtual environment at .venv
    echo.
    pause
    exit /b 1
)

:: 2. Check Node.js and npm
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not found in PATH.
    echo Please install Node.js v18+ or v20+ from https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] npm is not found in PATH.
    pause
    exit /b 1
)

:: 3. Check frontend dependencies
if not exist "%PROJECT_ROOT%frontend\node_modules" (
    echo [INFO] frontend\node_modules not found. Installing frontend dependencies...
    cd /d "%PROJECT_ROOT%frontend"
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install failed.
        pause
        exit /b 1
    )
    cd /d "%PROJECT_ROOT%"
)

:: 4. Check configuration file (.env)
if not exist "%PROJECT_ROOT%.env" (
    if exist "%PROJECT_ROOT%.env.example" (
        echo [INFO] Creating .env from .env.example...
        copy "%PROJECT_ROOT%.env.example" "%PROJECT_ROOT%.env" >nul
    )
)

:: 5. Check cloudflared
set "CLOUDFLARED_EXISTS=0"
where cloudflared >nul 2>&1
if %errorlevel% equ 0 set "CLOUDFLARED_EXISTS=1"
if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" set "CLOUDFLARED_EXISTS=1"
if exist "C:\Program Files\cloudflared\cloudflared.exe" set "CLOUDFLARED_EXISTS=1"

if "%CLOUDFLARED_EXISTS%"=="0" (
    echo [WARN] cloudflared is not installed.
    echo        Local services will start normally, but public tunnel will be unavailable.
    echo        To enable Cloudflare Tunnel: winget install Cloudflare.cloudflared
    echo.
)

:: 6. Launch Python Deployment Orchestrator
"%PROJECT_ROOT%.venv\Scripts\python.exe" scripts\deploy_manager.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Deployment manager exited with an error.
    pause
)
