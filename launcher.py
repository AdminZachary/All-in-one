import subprocess
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
