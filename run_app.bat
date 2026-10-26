@echo off
title SochnaSetu AI Launcher
cd /d "%~dp0"

echo ========================================================
echo   SochnaSetu AI -- Notice-to-Action Assistant (PS02)
echo ========================================================
echo.
echo Launching SochnaSetu AI via Unified Windows Lifecycle Launcher...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_sochnasetu.ps1"
if %errorlevel% neq 0 (
    echo.
    echo [FALLBACK] PowerShell launcher encountered an issue. Falling back to start_all.bat...
    call "%~dp0start_all.bat"
)
