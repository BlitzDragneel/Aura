@echo off
cd /d "%~dp0\..\.."
echo Cancelling every order and closing every position (bots AND Bridge kill switch)...
python -m edges.bots kill
pause
