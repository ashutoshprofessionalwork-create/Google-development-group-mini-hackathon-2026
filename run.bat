@echo off
echo Starting VayuNetra Backend and Frontend...
cd /d "%~dp0"

echo Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "VayuNetra Backend API" cmd /k "cd backend && python -m uvicorn main:app --reload"

echo Waiting 2 seconds for backend initialization...
timeout /t 2 /nobreak >nul

echo Opening VayuNetra Clean Air Portal in default browser...
start "" "frontend\frontend.html"

echo VayuNetra is live!
