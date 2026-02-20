from __future__ import annotations

import contextlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import api_router
from backend.storage.setup import setup_environment
from backend.utils.config import ROOT_DIR
from backend.utils.logger import app_logger

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app_logger.info("Starting up All-in-one Backend MVP...")
    setup_environment()
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
    # Serve index.html
    return FileResponse(ROOT_DIR / "1.html")

app.mount("/", StaticFiles(directory=ROOT_DIR, html=False), name="static")

if __name__ == "__main__":
    import uvicorn
    from backend.utils.config import HOST, PORT
    uvicorn.run(app, host=HOST, port=PORT)
