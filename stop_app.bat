@echo off
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0stop_app_background.ps1"
exit /b 0
