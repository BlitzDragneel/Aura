@echo off
REM OMEGA Recorder on Windows: records only while this window is open and the PC is awake.
cd /d %~dp0
if not exist venv ( py -3 -m venv venv && venv\Scripts\pip install -r requirements.txt )
set OMEGA_DB=%~dp0omega_recorder.sqlite
venv\Scripts\python -m omega_recorder selfcheck
venv\Scripts\python -m omega_recorder serve
