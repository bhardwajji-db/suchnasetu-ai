@echo off
setlocal enabledelayedexpansion
title SochnaSetu AI Launcher

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: 1. Verify Python virtual environment
if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found at .venv\Scripts\python.exe
    echo Please run scripts\setup.ps1 first.
    pause
    exit /b 1
)

:: 2. Launch through deterministic process supervisor
"%PROJECT_ROOT%.venv\Scripts\python.exe" scripts\process_supervisor.py %*




