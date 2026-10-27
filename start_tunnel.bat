@echo off
setlocal enabledelayedexpansion
title SuchnaSetu AI — Cloudflare Tunnel Production Deploy

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe
    pause
    exit /b 1
)

"%PROJECT_ROOT%.venv\Scripts\python.exe" scripts\launch_tunnel.py %*

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Tunnel launcher encountered an error.
    pause
)
