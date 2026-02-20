import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

if getattr(sys, 'frozen', False):
    EXEC_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    EXEC_DIR = Path(__file__).resolve().parent.parent.parent
    BUNDLE_DIR = EXEC_DIR

# Storage configuration
DATA_DIR = EXEC_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"
OUTPUTS_DIR = DATA_DIR / "outputs"
LOGS_DIR = EXEC_DIR / "logs"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "sqlite.db"

# Server configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "127.0.0.1")
