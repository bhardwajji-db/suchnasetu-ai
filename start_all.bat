@echo off
setlocal enabledelayedexpansion
title SochnaSetu AI Launcher

echo ======================================================================
echo             SOCHNASETU AI -- FULL-STACK SERVICES LAUNCHER
echo                 Notice-to-Action Accessibility Assistant
echo ======================================================================
echo.

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

:: 1. Check Python virtual environment
if not exist "%PROJECT_ROOT%.venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found at .venv\Scripts\python.exe
    echo Please run scripts\setup.ps1 first.
    pause
    exit /b 1
)

:: 2. Check and Start Ollama Server
echo [1/3] Checking Ollama Local AI Server (http://127.0.0.1:11434)...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo       Ollama server is not running. Starting ollama serve...
    where ollama >nul 2>&1
    if %errorlevel% equ 0 (
        start "Ollama AI Server" /min ollama serve
        timeout /t 3 /nobreak >nul
    ) else if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        start "Ollama AI Server" /min "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
        timeout /t 3 /nobreak >nul
    ) else (
        echo [WARNING] Ollama executable not found in PATH or standard location.
        echo           The app will run in fallback rule-based mode.
    )
) else (
    echo       Ollama server is already running and responsive.
)

:: 3. Launch FastAPI Backend Daemon
echo [2/3] Launching FastAPI Backend Server on http://127.0.0.1:8000...
start "SochnaSetu Backend (FastAPI)" cmd /k "title SochnaSetu Backend && cd /d "%PROJECT_ROOT%" && call .venv\Scripts\activate.bat && python -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000"

:: 4. Launch React 19 Frontend
echo [3/3] Launching React 19 + Vite Frontend on http://127.0.0.1:5173...
start "SochnaSetu Frontend (React/Vite)" cmd /k "title SochnaSetu Frontend && cd /d "%PROJECT_ROOT%frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

:: 5. Wait for servers to spin up and open browser
echo.
echo Waiting 4 seconds for services to initialize...
ping -n 5 127.0.0.1 >nul

echo Opening browser at http://localhost:5173...
start http://localhost:5173

echo.
echo ======================================================================
echo  All services launched successfully!
echo   * React Frontend: http://localhost:5173
echo   * FastAPI Backend: http://127.0.0.1:8000
echo   * API Docs: http://127.0.0.1:8000/docs
echo   * Ollama Server: http://127.0.0.1:11434
echo ======================================================================
echo Press any key to exit this launcher window (services keep running).
pause >nul
