@echo off
cd /d "%~dp0"
echo [Admin] Starting Streamlit admin panel...
:: Streamlit automatically opens the browser, so we just run the command
streamlit run app.py
pause
