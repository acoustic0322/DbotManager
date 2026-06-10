@echo off
echo ============================================================
echo   NUCLEAR FORCE STOP: Killing all automation processes
echo ============================================================
echo.
echo Stopping Python processes...
taskkill /F /IM python.exe /T
echo.
echo Stopping IXBrowser zombie chrome processes...
python -c "import psutil; [p.kill() for p in psutil.process_iter(['name', 'cmdline']) if 'chrome' in p.info['name'].lower() and p.info['cmdline'] and any('ixbrowser-resources' in str(arg).lower() for arg in p.info['cmdline'])]" >nul 2>&1
echo.
echo Clearing Global Command Table in DB...
python -c "from modules.mutual_follow.db_manager import DBManager; db = DBManager(); db.clear_global_command(); db.reset_all_in_use()"
echo.
echo ============================================================
echo   All processes terminated and DB cleared.
echo   Please restart worker_service.py manually.
echo ============================================================
pause
