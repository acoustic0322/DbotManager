@echo off
setlocal
cd /d "%~dp0"

echo ======================================================
echo   Twitter Automation FORCE RESET (v2.1.4 - CLEAN)
echo ======================================================
echo.
echo Killing all running python processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM py.exe /T >nul 2>&1
echo Killing all IXBrowser zombie chrome processes...
python -c "import psutil; [p.kill() for p in psutil.process_iter(['name', 'cmdline']) if 'chrome' in p.info['name'].lower() and p.info['cmdline'] and any('ixbrowser-resources' in str(arg).lower() for arg in p.info['cmdline'])]" >nul 2>&1

echo Cleaning up PID locks...
del /Q worker_*.pid >nul 2>&1
del /Q worker_*.lock >nul 2>&1
del /Q C:\temp\worker_*.lock >nul 2>&1

echo Waiting 5 seconds before restart...
timeout /t 5

echo Starting fresh worker service...
where python >nul 2>nul
if %errorlevel% == 0 (
    python worker_service.py
) else (
    py worker_service.py
)

pause
