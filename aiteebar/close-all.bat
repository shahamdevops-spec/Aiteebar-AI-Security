@echo off
REM Force close all CMD windows and Node processes
REM Run this as Administrator for best results

echo.
echo ========================================
echo   Aiteebar - Force Close All Processes
echo ========================================
echo.

REM Close all Node.js processes (frontend/backend dev servers)
echo [1/4] Closing Node.js processes...
taskkill /F /IM node.exe /T 2>nul
if errorlevel 1 (
    echo     No Node processes found
) else (
    echo     ✓ Node processes closed
)

REM Close all Python processes (backend)
echo [2/4] Closing Python processes...
taskkill /F /IM python.exe /T 2>nul
if errorlevel 1 (
    echo     No Python processes found
) else (
    echo     ✓ Python processes closed
)

REM Close all CMD windows
echo [3/4] Closing CMD windows...
taskkill /F /IM cmd.exe /T 2>nul
if errorlevel 1 (
    echo     No CMD windows found
) else (
    echo     ✓ CMD windows closed
)

REM Close all Powershell windows
echo [4/4] Closing PowerShell windows...
taskkill /F /IM powershell.exe /T 2>nul
if errorlevel 1 (
    echo     No PowerShell windows found
) else (
    echo     ✓ PowerShell windows closed
)

echo.
echo ========================================
echo   All processes closed successfully!
echo ========================================
echo.
echo Press any key to exit...
pause >nul
exit /b 0
