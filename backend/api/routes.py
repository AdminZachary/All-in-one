import uuid
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.models.schemas import CloneVoiceResponse, CreateJobRequest, CreateJobResponse, JobStatusResponse
from backend.storage.db import save_voice, save_job, get_job, get_voice
from backend.services.job_service import JobService
from backend.utils.logger import app_logger

api_router = APIRouter()

def build_script(script_mode: str, script_input: str) -> str:
    if script_mode == "manual":
        return script_input
    return (
        f"（AI基于主题\"{script_input}\"生成）:\n"
        "大家好。\n"
        "欢迎来到空间计算时代。\n"
        "你看到的是一体化本地整合包的生成结果。\n"
        "系统默认使用 Wan2GP 保障稳定，并可智能回退。"
    )

@api_router.post("/voice/clone", response_model=CloneVoiceResponse)
def clone_voice():
    voice_id = f"voice_{uuid.uuid4().hex[:8]}"
    save_voice(voice_id, engine="wan2gp", status="ready")
    app_logger.info(f"Created new voice clone: {voice_id}")
    return CloneVoiceResponse(voice_id=voice_id, engine="wan2gp")

@api_router.post("/jobs", response_model=CreateJobResponse)
def create_job(payload: CreateJobRequest, background_tasks: BackgroundTasks):
    voice_record = get_voice(payload.voice_id)
    if not voice_record:
        raise HTTPException(status_code=400, detail="无效 voice_id，请先完成声音克隆")

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    generated_script = build_script(payload.script_mode, payload.script_input)
    
    # Auto logic: Default to wan2gp unless they asked for infinitetalk.
    # The job service dynamically adjusts this.
    initial_engine = "wan2gp" if payload.preferred_engine == "auto" else payload.preferred_engine
    
    job_data = {
        "job_id": job_id,
        "voice_id": payload.voice_id,
        "avatar_url": payload.avatar_url,
        "script_mode": payload.script_mode,
        "script_input": payload.script_input,
        "preferred_engine": initial_engine,
        "selected_engine": initial_engine,
        "wangp_model": payload.wangp_model,
        "status": "queued",
        "progress": 0,
        "message": "排队中...",
    }
    
    save_job(job_data)
    app_logger.info(f"Registered new job: {job_id} with preferred engine {initial_engine}")
    
    # Dispatch worker to process the job in background
    background_tasks.add_task(
        JobService.process_job_async,
        job_id=job_id,
        voice_id=payload.voice_id,
        avatar_url=payload.avatar_url,
        script_text=generated_script,
        preferred_engine=initial_engine,
        wangp_model=payload.wangp_model
    )

    return CreateJobResponse(job_id=job_id, selected_engine=initial_engine, wangp_model=payload.wangp_model)

@api_router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str):
    record = get_job(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="任务不存在")

    return JobStatusResponse(
        job_id=job_id,
        status=record["status"],
        progress=record["progress"],
        message=record["message"],
        selected_engine=record["selected_engine"],
        wangp_model=record.get("wangp_model", "Wan t2v 1.3B"),
        fallback_reason=record.get("fallback_reason"),
        generated_script=record.get("generated_script") if record["status"] == "completed" else None,
        result_url=record.get("result_url") if record["status"] == "completed" else None
    )

from fastapi.responses import FileResponse
from backend.utils.config import OUTPUTS_DIR

@api_router.get("/jobs/{job_id}/result")
def get_job_result(job_id: str):
    record = get_job(job_id)
    if not record or record["status"] != "completed":
        raise HTTPException(status_code=404, detail="Result not ready or job not found")
        
    return {"status": "ready", "url": f"/api/jobs/{job_id}/download", "filename": f"{job_id}.mp4"}

@api_router.get("/jobs/{job_id}/download")
def download_job_result(job_id: str):
    record = get_job(job_id)
    if not record or record["status"] != "completed":
        raise HTTPException(status_code=404, detail="Result not ready or job not found")
    
    # The file path is defined by the engine adaptors, typically in OUTPUTS_DIR
    # We can infer it or just search the outputs dir:
    engine = record.get("selected_engine", "wan2gp")
    expected_path = OUTPUTS_DIR / f"{job_id}_{engine}.mp4"
    
    if not expected_path.exists():
        raise HTTPException(status_code=404, detail="Video file is missing from disk")
        
    return FileResponse(
        path=expected_path,
        filename=f"InfiniteTalk_{job_id}.mp4",
        media_type="video/mp4"
    )
