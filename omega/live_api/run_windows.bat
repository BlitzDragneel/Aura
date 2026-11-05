@echo off
REM OMEGA Live API on this PC: http://127.0.0.1:8787  (docs: http://127.0.0.1:8787/docs)
REM Optional: set TWELVEDATA_API_KEY=your_key   (enables forex candles)
cd /d %~dp0
if not exist .venv ( py -3 -m venv .venv && .venv\Scripts\pip install -r requirements.txt )
.venv\Scripts\python -m omega_live
