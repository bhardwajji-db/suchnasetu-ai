@echo off
setlocal enabledelayedexpansion
title SochnaSetu AI — Production Unified Launcher

echo ======================================================================
echo             SOCHNASETU AI -- PRODUCTION UNIFIED LAUNCHER
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

:: 2. Build Frontend Production Assets if needed
if not exist "%PROJECT_ROOT%frontend\dist\index.html" (
    echo [1/3] Compiling React 19 production bundle with Vite...
    cd /d "%PROJECT_ROOT%frontend"
    call npm run build
    if %errorlevel% neq 0 (
        echo [ERROR] Frontend compilation failed.
        pause
        exit /b 1
    )
    cd /d "%PROJECT_ROOT%"
) else (
    echo [1/3] Frontend production bundle verified at frontend\dist.
)

:: 3. Check and Start Ollama AI Server
echo [2/3] Checking Ollama Local AI Server (http://127.0.0.1:11434)...
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo       Ollama server is not running. Attempting to start ollama serve...
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

:: 4. Detect local Wi-Fi IP
set "WIFI_IP=127.0.0.1"
for /f "usebackq tokens=*" %%i in (`powershell -NoProfile -Command "(Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias '*Wi-Fi*','*Wireless*' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"`) do set "WIFI_IP=%%i"

:: 5. Launch Unified FastAPI Server (Serves API on /api and SPA UI on /)
echo [3/3] Launching Unified Production Server on port 8000...
echo.
echo ======================================================================
echo  Production Server Running!
echo   * Local PC Access:      http://localhost:8000
echo   * On Phone (Same WiFi): http://%WIFI_IP%:8000
echo   * API Interactive Docs: http://%WIFI_IP%:8000/docs
echo   * Ollama Model Server:  http://127.0.0.1:11434
echo ======================================================================
echo.

start http://localhost:8000

call .venv\Scripts\activate.bat
python -m uvicorn notice2action.api.server:app --app-dir src --host 0.0.0.0 --port 8000 --workers 2
