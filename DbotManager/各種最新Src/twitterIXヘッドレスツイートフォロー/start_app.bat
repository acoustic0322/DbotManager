@echo off
title D-Bot Admin Panel Launcher
echo ============================================
echo  Core Service Manager - Starting UI
echo ============================================
echo.

cd /d "%~dp0"

echo [1/1] Launching Management Hub...
streamlit run app.py

pause
