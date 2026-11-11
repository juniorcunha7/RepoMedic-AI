@echo off
cd /d "%~dp0"
echo RepoMedic AI ^| Launching local dashboard...
start "RepoMedic AI Dashboard" "http://127.0.0.1:8000/"
py -3 -m uvicorn repomedic.api:app --host 127.0.0.1 --port 8000
if errorlevel 1 (
 echo.
 echo Install server dependencies using: py -3 -m pip install -e ".[api,dev]"
 pause
)
