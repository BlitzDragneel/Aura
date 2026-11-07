@echo off
cd /d "%~dp0\..\.."
python -m edges.bots run --mode testnet
pause
