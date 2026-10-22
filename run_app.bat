@echo off
title SochnaSetu AI Launcher
echo ========================================================
echo   SochnaSetu AI -- Notice-to-Action Assistant (PS02)
echo ========================================================
echo.
echo [1/3] Starting FastAPI Backend on port 8000 in new terminal...
start "SochnaSetu AI - Backend API" cmd /k "cd /d "%~dp0" && .\.venv\Scripts\python.exe -m uvicorn notice2action.api.server:app --app-dir src --host 127.0.0.1 --port 8000"

timeout /t 2 /nobreak >nul

echo [2/3] Starting Vite React Frontend on port 5173 in new terminal...
start "SochnaSetu AI - React Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

timeout /t 3 /nobreak >nul

echo [3/3] Opening application in default web browser...
start http://127.0.0.1:5173

echo.
echo Application launched!
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://127.0.0.1:5173
echo.
echo Keep both terminal windows open while using SochnaSetu AI.
echo Close the terminal windows when done.
pause

