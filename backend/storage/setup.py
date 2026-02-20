from backend.utils.config import DATA_DIR, UPLOADS_DIR, CACHE_DIR, OUTPUTS_DIR, LOGS_DIR
from backend.storage.db import init_db
from backend.utils.logger import boot_logger

def setup_environment():
    """Ensure all required directories and DB are setup."""
    boot_logger.info("Starting environment setup...")
    for directory in [DATA_DIR, UPLOADS_DIR, CACHE_DIR, OUTPUTS_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        boot_logger.info(f"Ensured directory exists: {directory}")
        
    init_db()
    boot_logger.info("Environment setup complete.")

if __name__ == "__main__":
    setup_environment()
