@echo off
echo Starting Plant Tracker...

start "Plant Tracker - Backend" cmd /k "cd /d "%~dp0server" && .venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"

start "Plant Tracker - Frontend" cmd /k "cd /d "%~dp0plant-tracker-client" && npm run dev"

echo Both servers are starting in separate windows.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:8080
