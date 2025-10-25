@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ===============================================
REM start_login_profiles_ascii.bat
REM ASCII-only to avoid mojibake on Windows cmd.exe
REM Requirements:
REM   - login_no_proxy.py in the same folder
REM   - profiles.txt (one Firefox profile path per line)
REM Usage:
REM   Manual login:  start_login_profiles_ascii.bat
REM   Auto login  :  start_login_profiles_ascii.bat your_id_or_email your_password
REM ===============================================

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

where python >nul 2>&1
if errorlevel 1 (
  echo [ERR] Python not found. Use "py -3" or add Python to PATH.
  echo Example:  py -3 login_no_proxy.py --profiles profiles.txt
  pause
  exit /b 1
)

if not exist "login_no_proxy.py" (
  echo [ERR] login_no_proxy.py not found in this folder.
  pause
  exit /b 1
)

set "PROFILE_LIST=profiles.txt"
if not exist "%PROFILE_LIST%" (
  echo [ERR] profiles.txt not found.
  echo Create a file with one Firefox profile path per line.
  echo Example:
  echo   C:\Users\YOU\AppData\Roaming\Mozilla\Firefox\Profiles\xxxx.default
  echo   C:\Users\YOU\AppData\Roaming\Mozilla\Firefox\Profiles\zzzz.Profile 185
  pause
  exit /b 1
)

set "USER_ARG="
set "PASS_ARG="
if not "%~1"=="" set "USER_ARG=--user %~1"
if not "%~2"=="" set "PASS_ARG=--password %~2"

echo.
echo === Login Helper (no proxy) ===
echo   profiles: %PROFILE_LIST%
if defined USER_ARG (
  echo   mode    : Auto input (ID/PW provided)
) else (
  echo   mode    : Manual (UI login)
)
echo.

python "login_no_proxy.py" --profiles "%PROFILE_LIST%" %USER_ARG% %PASS_ARG%
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
  echo [DONE] Finished.
) else (
  echo [WARN] Exit code: %RC%
)
echo.
pause

popd
endlocal
