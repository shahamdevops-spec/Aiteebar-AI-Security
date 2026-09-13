@echo off
echo ========================================
echo Opening Backend and Frontend...
echo ========================================
start cmd /k "cd "C:\Users\Ntech\Desktop\Aiteebar AI Security\aiteebar" && call start-backend.bat"
start cmd /k "cd "C:\Users\Ntech\Desktop\Aiteebar AI Security\aiteebar" && call start-frontend.bat"
echo.
echo ✓ Both servers starting in separate windows...
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:3000
pause
