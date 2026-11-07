@echo off
cd /d "%~dp0\..\.."
python -m edges.bots run --mode paper
pause
