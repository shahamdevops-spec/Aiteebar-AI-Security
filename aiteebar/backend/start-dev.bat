@echo off
REM Start Aiteebar Backend in development mode

cls
echo.
echo ================================================================================
echo                   AITEEBAR - BACKEND (Development)
echo ================================================================================
echo.

REM Ensure we're in the backend directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

REM Start backend with uvicorn
echo Starting backend server on http://localhost:8000...
echo Press Ctrl+C to stop
echo.
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
