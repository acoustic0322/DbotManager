@echo off

cd /d C:\Users\MT4ver2-a03-0IVGULYn\Desktop\DbotManager\Src\DbotManager\ŠeŽíÅVSrc\python

if not exist log mkdir log

set YYYY=%date:~0,4%
set MM=%date:~5,2%
set DD=%date:~8,2%

set HH=%time:~0,2%
set NN=%time:~3,2%

REM 1Œ…ŽžŠÔ‘Îô
set HH=%HH: =0%

set LOGFILE=log\log_check_refresh_%YYYY%%MM%%DD%_%HH%%NN%.txt

echo START %date% %time% >> %LOGFILE%

python tweet.py mode=check_refresh debug=true >> %LOGFILE% 2>&1

echo END %date% %time% >> %LOGFILE%