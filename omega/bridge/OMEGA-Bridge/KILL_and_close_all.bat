@echo off
cd /d %~dp0
echo KILL SWITCH: blocks every new order and closes all positions on both venues.
python -c "from omega_bridge.core import Bridge; print(Bridge().kill(True, flatten=True))"
pause
