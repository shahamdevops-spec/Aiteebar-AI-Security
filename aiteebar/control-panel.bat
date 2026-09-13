@echo off
setlocal enabledelayedexpansion
color 0A
cls

:menu
cls
echo.
echo ================================================================================
echo                    AITEEBAR - PROCESS CONTROL PANEL
echo ================================================================================
echo.
echo   Select an option:
echo.
echo   1) Close ALL processes (Node, Python, CMD, PowerShell)
echo   2) Close Backend (Python only)
echo   3) Close Frontend (Node only)
echo   4) Close CMD windows only
echo   5) Close PowerShell windows only
echo   6) Show running processes
echo   7) Exit
echo.
echo ================================================================================
echo.

set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto close_all
if "%choice%"=="2" goto close_backend
if "%choice%"=="3" goto close_frontend
if "%choice%"=="4" goto close_cmd
if "%choice%"=="5" goto close_powershell
if "%choice%"=="6" goto show_processes
if "%choice%"=="7" goto exit_menu

echo Invalid choice. Please try again.
timeout /t 2 >nul
goto menu

:close_all
cls
echo.
echo [*] Closing all processes...
echo.
echo     Closing Node processes...
taskkill /F /IM node.exe /T 2>nul
echo     Closing Python processes...
taskkill /F /IM python.exe /T 2>nul
echo     Closing CMD windows...
taskkill /F /IM cmd.exe /T 2>nul
echo     Closing PowerShell...
taskkill /F /IM powershell.exe /T 2>nul
echo.
echo [✓] All processes closed!
echo.
pause
goto menu

:close_backend
cls
echo.
echo [*] Closing Backend (Python)...
taskkill /F /IM python.exe /T
if errorlevel 1 (
    echo [!] No Python processes found
) else (
    echo [✓] Backend processes closed!
)
echo.
pause
goto menu

:close_frontend
cls
echo.
echo [*] Closing Frontend (Node)...
taskkill /F /IM node.exe /T
if errorlevel 1 (
    echo [!] No Node processes found
) else (
    echo [✓] Frontend processes closed!
)
echo.
pause
goto menu

:close_cmd
cls
echo.
echo [*] Closing CMD windows...
taskkill /F /IM cmd.exe /T
if errorlevel 1 (
    echo [!] No CMD windows found
) else (
    echo [✓] CMD windows closed!
)
echo.
pause
goto menu

:close_powershell
cls
echo.
echo [*] Closing PowerShell windows...
taskkill /F /IM powershell.exe /T
if errorlevel 1 (
    echo [!] No PowerShell windows found
) else (
    echo [✓] PowerShell windows closed!
)
echo.
pause
goto menu

:show_processes
cls
echo.
echo [*] Running processes:
echo.
echo --- Node.js (Frontend) ---
tasklist /FI "IMAGENAME eq node.exe" 2>nul
if errorlevel 1 echo     (none)
echo.
echo --- Python (Backend) ---
tasklist /FI "IMAGENAME eq python.exe" 2>nul
if errorlevel 1 echo     (none)
echo.
echo --- CMD Windows ---
tasklist /FI "IMAGENAME eq cmd.exe" 2>nul
if errorlevel 1 echo     (none)
echo.
echo --- PowerShell ---
tasklist /FI "IMAGENAME eq powershell.exe" 2>nul
if errorlevel 1 echo     (none)
echo.
pause
goto menu

:exit_menu
cls
echo.
echo Exiting Control Panel...
echo.
timeout /t 1 >nul
exit /b 0
