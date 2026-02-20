import PyInstaller.__main__
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def build_executable():
    print("====================================")
    print(" Building Backend EXE (Console)     ")
    print("====================================")
    
    # Bundle the backend with console enabled so pipes work
    PyInstaller.__main__.run([
        str(ROOT_DIR / 'backend' / 'main.py'),
        '--name=All-in-one_backend',
        '--onefile',
        '--console',
        f'--add-data={ROOT_DIR / "1.html"};.',
        '--exclude-module=data', 
        '--exclude-module=logs',
        '--hidden-import=uvicorn.logging',
        '--hidden-import=uvicorn.loops',
        '--hidden-import=uvicorn.loops.auto',
        '--hidden-import=uvicorn.protocols',
        '--hidden-import=uvicorn.protocols.http',
        '--hidden-import=uvicorn.protocols.http.auto',
        '--hidden-import=uvicorn.protocols.websockets',
        '--hidden-import=uvicorn.protocols.websockets.auto',
        '--hidden-import=uvicorn.lifespan',
        '--hidden-import=uvicorn.lifespan.on',
        '--hidden-import=git',
        '--collect-all=git',
        '--collect-all=huggingface_hub',
        '--copy-metadata=huggingface_hub',
        '--clean'
    ])
    
    print("====================================")
    print(" Building Launcher EXE (Hidden)     ")
    print("====================================")
    
    # Create the launcher script on the fly
    launcher_code = '''import subprocess
import sys
import os
from pathlib import Path

# When frozen, run the backend from the same directory
if getattr(sys, "frozen", False):
    base_dir = Path(sys.executable).parent
else:
    base_dir = Path(__file__).parent

backend_exe = base_dir / "All-in-one_backend.exe"

if backend_exe.exists():
    # CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen([str(backend_exe)], creationflags=0x08000000)
'''
    launcher_path = ROOT_DIR / 'launcher.py'
    launcher_path.write_text(launcher_code)
    
    PyInstaller.__main__.run([
        str(launcher_path),
        '--name=All-in-one',
        '--onefile',
        '--noconsole',
        '--clean'
    ])
    
    import shutil
    
    print("====================================")
    print(" Assembling Portable Distribution    ")
    print("====================================")
    
    dist_dir = ROOT_DIR / 'dist'
    dist_wan = dist_dir / 'wan2gp_core'
    
    if dist_wan.exists():
        shutil.rmtree(dist_wan)
    
    shutil.copytree(
        ROOT_DIR / 'wan2gp_core',
        dist_wan,
        ignore=shutil.ignore_patterns('.git', 'venv', '__pycache__')
    )
    
    shutil.copy(ROOT_DIR / 'install_wan2gp.bat', dist_dir / 'install_wan2gp.bat')
    shutil.copy(ROOT_DIR / 'README.md', dist_dir / 'README.md')
    
    print("Build complete. Please distribute the `dist` folder.")

if __name__ == "__main__":
    build_executable()
