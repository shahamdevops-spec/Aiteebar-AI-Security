@echo off
REM Start Aiteebar fresh - closes old processes and starts new ones
color 0A
cls

echo.
echo ================================================================================
echo                   AITEEBAR - START FRESH SETUP
echo ================================================================================
echo.

REM Close all existing processes
echo [1/5] Closing existing processes...
taskkill /F /IM node.exe /T 2>nul
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM cmd.exe /T 2>nul
echo     ✓ Old processes closed
echo.

REM Start Backend
echo [2/5] Starting Backend server...
cd backend
start "Aiteebar Backend" cmd /k "python -m uvicorn app.main:app --reload"
echo     ✓ Backend starting on http://localhost:8000
timeout /t 3 >nul
echo.

REM Seed users
echo [3/5] Seeding demo users...
start "Aiteebar Seed Users" cmd /k "python scripts/seed_users.py"
timeout /t 3 >nul
echo     ✓ Demo users seeding
echo.

REM Navigate back to frontend
cd ..

REM Start Frontend
echo [4/5] Starting Frontend server...
cd frontend
start "Aiteebar Frontend" cmd /k "npm run dev"
echo     ✓ Frontend starting on http://localhost:3000
echo.

REM Done
echo [5/5] Setup complete!
echo.
echo ================================================================================
echo   ✓ Backend:  http://localhost:8000
echo   ✓ Frontend: http://localhost:3000
echo   ✓ Login:    http://localhost:3000/login
echo ================================================================================
echo.
echo Demo Credentials:
echo   Admin:   admin@aiteebar.ai / Admin@123
echo   Analyst: analyst@aiteebar.ai / Analyst@123
echo   Viewer:  viewer@aiteebar.ai / Viewer@123
echo.
echo Your terminal windows are starting. Wait for all to fully load.
echo.
pause
