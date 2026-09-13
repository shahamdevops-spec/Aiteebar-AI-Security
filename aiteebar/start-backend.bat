@echo off
cd "C:\Users\Ntech\Desktop\Aiteebar AI Security\aiteebar\backend"
call venv\Scripts\activate
echo.
echo ========================================
echo Starting Backend Server...
echo ========================================
echo.
uvicorn app.main:app --reload
pause
