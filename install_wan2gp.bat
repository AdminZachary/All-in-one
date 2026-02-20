@echo off
echo ==========================================
echo   InfiniteTalk - Wan2GP Native Installer
echo ==========================================
echo This script will setup the heavy PyTorch environment and download Wan2GP models.
echo It will require approximately 10-30GB of space depending on the models.
echo.

cd /d "%~dp0"
if not exist "wan2gp_core" (
    echo [ERROR] Wan2GP core folder not found. Please ensure it is in the same folder as this script.
    pause
    exit /b
)

cd "wan2gp_core"

if not exist "venv" (
    echo [INFO] Creating portable Python Video Environment...
    python -m venv venv
)

echo [INFO] Activating environment...
call venv\Scripts\activate.bat

echo [INFO] Installing PyTorch (CUDA 13.0) - This is a very large download...
pip install torch==2.10.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

echo [INFO] Installing Wan2GP specific dependencies...
pip install -r requirements.txt

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo Wan2GP engine is now natively integrated.
echo Next time you generate a video in the UI, it will use your local GPU!
pause
