import PyInstaller.__main__
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

def build_executable():
    print("====================================")
    print(" Building All-in-one Standalone EXE ")
    print("====================================")
    
    # We bundle fastapi, uvicorn, and all custom scripts into a single file.
    # We must explicitly add 1.html so the frontend works offline inside the bundle.
    
    PyInstaller.__main__.run([
        str(ROOT_DIR / 'backend' / 'main.py'),
        '--name=All-in-one',
        '--onefile',
        '--console',
        f'--add-data={ROOT_DIR / "1.html"};.',
        # Exclude local dev/data folders from being bundled statically
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
        '--clean'
    ])
    
    print("Build complete. Please check the `dist` folder.")

if __name__ == "__main__":
    build_executable()
