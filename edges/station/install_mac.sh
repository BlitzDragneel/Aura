#!/bin/bash
# OMEGA Station installer for macOS (and Linux). Run once from inside the Aura folder: bash edges/station/install_mac.sh
set -e
cd "$(dirname "$0")/../.."
command -v python3 >/dev/null || { echo "Install Python 3.12 from python.org first."; exit 1; }
[ -d .venv ] || python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r edges/station/requirements.txt
if [ "$(uname)" = "Darwin" ]; then
  PL="$HOME/Library/LaunchAgents/com.omega.station.plist"
  cat > "$PL" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
 <key>Label</key><string>com.omega.station</string>
 <key>ProgramArguments</key><array><string>$PWD/.venv/bin/python</string><string>$PWD/edges/station/station.py</string></array>
 <key>WorkingDirectory</key><string>$PWD</string>
 <key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
 <key>StandardOutPath</key><string>$HOME/OMEGA-Station/stdout.log</string>
 <key>StandardErrorPath</key><string>$HOME/OMEGA-Station/stderr.log</string>
</dict></plist>
PLIST
  mkdir -p "$HOME/OMEGA-Station"
  launchctl unload "$PL" 2>/dev/null || true
  launchctl load "$PL"
  echo "Installed and running in the background (starts at login). Records: ~/OMEGA-Station  (stop: launchctl unload $PL)"
else
  echo "Start it with: .venv/bin/python edges/station/station.py   (records in ~/OMEGA-Station)"
fi
