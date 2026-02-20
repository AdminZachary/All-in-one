@echo off
setlocal enabledelayedexpansion

echo ==================================
echo  Starting InfiniteTalk & Wan2GP   
echo ==================================

netstat -ano | findstr :8000 | findstr LISTENING >nul
if %ERRORLEVEL% equ 0 (
    echo [Error] Port 8000 is already in use. Please free the port and try again.
    pause
    exit /b 1
)

if not exist .venv (
  echo =^> Creating Python virtual environment...
  py -m venv .venv
)

echo =^> Activating environment and installing dependencies...
call .venv\Scripts\activate
pip install -q -r requirements.txt

echo =^> Creating required directories...
if not exist data\uploads mkdir data\uploads
if not exist data\cache mkdir data\cache
if not exist data\outputs mkdir data\outputs
if not exist logs mkdir logs

echo =^> Starting backend server...
uvicorn backend.main:app --host 127.0.0.1 --port 8000
