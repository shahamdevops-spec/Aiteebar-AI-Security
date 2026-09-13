@echo off
REM Emergency: Force kill all CMD windows
REM This is the fastest way to close stuck CMD windows

echo Forcefully closing all CMD windows...
taskkill /F /IM cmd.exe /T
echo Done!
