@echo off
echo ==========================================
echo   InfiniteTalk - Wan2GP Native Installer
echo ==========================================
echo This script will setup the heavy PyTorch environment and download Wan2GP models.
echo It will require approximately 10-30GB of space depending on the models.
echo.
echo [!] This installation is completely ISOLATED in a Virtual Environment (venv).
echo [!] It will NOT affect or pollute your main system Python environment.
echo.

cd /d "%~dp0"
if not exist "wan2gp_core" (
    echo [ERROR] Wan2GP core folder not found. Please ensure it is in the same folder as this script.
    pause
    exit /b
)

cd "wan2gp_core"

if not exist "python_env\python.exe" (
    echo [INFO] Downloading Portable Python 3.10...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.10.11/python-3.10.11-embed-amd64.zip' -OutFile 'python_embed.zip'"
    
    echo [INFO] Extracting Portable Python...
    powershell -Command "Expand-Archive -Path 'python_embed.zip' -DestinationPath 'python_env' -Force"
    del python_embed.zip
    
    echo [INFO] Setting up pip module support...
    :: Enable site-packages in portable python
    powershell -Command "(Get-Content 'python_env\python310._pth') -replace '#import site', 'import site' | Set-Content 'python_env\python310._pth'"
    
    echo [INFO] Installing pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile 'get-pip.py'"
    python_env\python.exe get-pip.py
    del get-pip.py
)

set PYTHON_EXE=%~dp0wan2gp_core\python_env\python.exe
set PIP_EXE=%~dp0wan2gp_core\python_env\Scripts\pip.exe

if not exist "%PYTHON_EXE%" (
    echo [ERROR] Portable Python extraction failed.
    pause
    exit /b
)

echo [INFO] Installing PyTorch (CUDA 12.4) - This is a stable build (~3GB download)...
"%PIP_EXE%" install torch==2.5.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo [INFO] Installing Wan2GP specific dependencies...
"%PIP_EXE%" install -r requirements.txt

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo Wan2GP engine is now natively integrated.
echo Next time you generate a video in the UI, it will use your local GPU!
pause
