@echo off
REM OMEGA Station installer for Windows. Run once from inside the Aura folder: edges\station\install_windows.bat
cd /d "%~dp0\..\.."
where py >nul 2>nul || (echo Python is missing: install Python 3.12 from python.org and tick "Add to PATH", then run this again. & pause & exit /b 1)
if not exist .venv ( py -3 -m venv .venv )
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r edges\station\requirements.txt || (echo Package install failed. & pause & exit /b 1)
REM start automatically when you log in (a scheduled task; remove it with: schtasks /delete /tn "OMEGA Station" /f)
schtasks /create /tn "OMEGA Station" /tr "\"%CD%\edges\station\start_windows.bat\"" /sc onlogon /rl limited /f
echo.
echo Installed. Starting OMEGA Station now (a window opens; leave it open). It also starts by itself when you log in.
start "" "%CD%\edges\station\start_windows.bat"
pause
