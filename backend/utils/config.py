import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# Storage configuration
DATA_DIR = ROOT_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"
OUTPUTS_DIR = DATA_DIR / "outputs"
LOGS_DIR = ROOT_DIR / "logs"

DB_PATH = DATA_DIR / "sqlite.db"

# Server configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "127.0.0.1")
