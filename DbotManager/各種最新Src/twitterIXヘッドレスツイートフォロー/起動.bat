@echo off
cd /d %~dp0
echo ==========================================
echo    Twitter AI Automation Dashboard
echo ==========================================
echo Starting Streamlit Dashboard...
streamlit run app.py
pause
