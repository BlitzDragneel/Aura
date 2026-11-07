@echo off
cd /d "%~dp0\..\.."
python -m edges.bots backtest --strategy panic_h1 --from 2024-01-01
pause
