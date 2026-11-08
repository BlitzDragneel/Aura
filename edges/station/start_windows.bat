@echo off
title OMEGA Station - leave this window open
cd /d "%~dp0\..\.."
.venv\Scripts\python edges\station\station.py
pause
