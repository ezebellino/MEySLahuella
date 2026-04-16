@echo off
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0start_app_background.ps1"
exit /b 0
