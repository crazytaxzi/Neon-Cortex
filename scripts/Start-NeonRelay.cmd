@echo off
setlocal
set ROOT=%LOCALAPPDATA%\Neon_Cortex
"%ROOT%\.venv\Scripts\python.exe" -m neon_relay --config "%ROOT%\config\swarm.json" watch-github
pause
