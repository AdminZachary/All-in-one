from __future__ import annotations

import contextlib
import multiprocessing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import api_router
from backend.storage.setup import setup_environment
from backend.utils.config import BUNDLE_DIR
from backend.utils.logger import app_logger

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting up All-in-one Backend MVP...")
    setup_environment()
    from backend.utils.downloader import download_mock_models
    download_mock_models()
    yield
    # Shutdown
    app_logger.info("Shutting down All-in-one Backend MVP...")

app = FastAPI(title="All-in-one Local Backend", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health() -> dict:
    return {"ok": True}

app.include_router(api_router, prefix="/api")

@app.get("/")
def index() -> FileResponse:
    # Serve index.html from bundle
    return FileResponse(BUNDLE_DIR / "1.html")

app.mount("/", StaticFiles(directory=BUNDLE_DIR, html=False), name="static")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    import uvicorn
    from backend.utils.config import HOST, PORT
    try:
        uvicorn.run(app, host=HOST, port=PORT)
    except Exception as e:
        print(f"\n[ERROR] Failed to start server: {e}")
        print("[ERROR] Port 8000 might already be in use by another program or start.bat.")
        input("Press Enter to exit...")
