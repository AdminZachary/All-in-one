from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="All-in-one Local Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parent.parent


class CloneVoiceResponse(BaseModel):
    voice_id: str
    status: Literal["ready"] = "ready"
    engine: Literal["wan2gp", "infinitetalk"]


class CreateJobRequest(BaseModel):
    voice_id: str
    avatar_url: str
    script_mode: Literal["ai", "manual"]
    script_input: str = Field(min_length=1)
    preferred_engine: Literal["auto", "wan2gp", "infinitetalk"] = "auto"


class CreateJobResponse(BaseModel):
    job_id: str
    selected_engine: Literal["wan2gp", "infinitetalk"]


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    progress: int
    message: str
    selected_engine: Literal["wan2gp", "infinitetalk"]
    generated_script: str | None = None


VOICE_REGISTRY: dict[str, dict] = {}
JOBS: dict[str, dict] = {}


def choose_engine(preferred_engine: str) -> Literal["wan2gp", "infinitetalk"]:
    """Default to Wan2GP for stability; InfiniteTalk can be explicitly selected."""
    if preferred_engine == "infinitetalk":
        return "infinitetalk"
    return "wan2gp"


def build_script(script_mode: str, script_input: str) -> str:
    if script_mode == "manual":
        return script_input
    return (
        f"（AI基于主题\"{script_input}\"生成）:\n"
        "大家好。\n"
        "欢迎来到空间计算时代。\n"
        "你看到的是一体化本地整合包的生成结果。\n"
        "系统默认使用 Wan2GP 保障稳定，并可切换 InfiniteTalk 提升质量。"
    )


def compute_job_progress(created_at: datetime) -> tuple[int, str, Literal["queued", "running", "completed"]]:
    seconds = max((datetime.now(timezone.utc) - created_at).total_seconds(), 0)
    if seconds < 0.8:
        return 10, "解析空间特征...", "queued"
    if seconds < 1.6:
        return 30, "音频预处理...", "running"
    if seconds < 2.4:
        return 50, "口型驱动...", "running"
    if seconds < 3.2:
        return 70, "面部光影重绘...", "running"
    if seconds < 4.0:
        return 90, "渲染帧...", "running"
    return 100, "完成", "completed"


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/voice/clone", response_model=CloneVoiceResponse)
def clone_voice() -> CloneVoiceResponse:
    voice_id = f"voice_{uuid.uuid4().hex[:8]}"
    VOICE_REGISTRY[voice_id] = {"created_at": datetime.now(timezone.utc)}
    return CloneVoiceResponse(voice_id=voice_id, engine="wan2gp")


@app.post("/api/jobs", response_model=CreateJobResponse)
def create_job(payload: CreateJobRequest) -> CreateJobResponse:
    if payload.voice_id not in VOICE_REGISTRY:
        raise HTTPException(status_code=400, detail="无效 voice_id，请先完成声音克隆")

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    selected_engine = choose_engine(payload.preferred_engine)
    JOBS[job_id] = {
        "created_at": datetime.now(timezone.utc),
        "selected_engine": selected_engine,
        "generated_script": build_script(payload.script_mode, payload.script_input),
    }
    return CreateJobResponse(job_id=job_id, selected_engine=selected_engine)


@app.get("/api/jobs/{job_id}", response_model=JobStatusResponse)
def get_job(job_id: str) -> JobStatusResponse:
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="任务不存在")

    record = JOBS[job_id]
    progress, message, status = compute_job_progress(record["created_at"])
    return JobStatusResponse(
        job_id=job_id,
        status=status,
        progress=progress,
        message=message,
        selected_engine=record["selected_engine"],
        generated_script=record["generated_script"] if status == "completed" else None,
    )


@app.get("/")
def index() -> FileResponse:
    return FileResponse(ROOT / "1.html")


app.mount("/", StaticFiles(directory=ROOT, html=False), name="static")
