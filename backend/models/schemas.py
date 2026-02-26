from pydantic import BaseModel, Field
from typing import Literal

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
    wangp_model: str = "Wan t2v 1.3B" # Changed to accept any string without validation failure

class CreateJobResponse(BaseModel):
    job_id: str
    selected_engine: Literal["wan2gp", "infinitetalk"]
    wangp_model: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    progress: int
    message: str
    selected_engine: str
    wangp_model: str
    fallback_reason: str | None = None
    generated_script: str | None = None
    result_url: str | None = None

class ModelStatusResponse(BaseModel):
    model_id: str
    status: Literal["ready", "not_downloaded", "downloading"]
    progress: int

class ModelDownloadRequest(BaseModel):
    model_id: str

class ModelDownloadProgressResponse(BaseModel):
    model_id: str
    status: Literal["ready", "not_downloaded", "downloading"]
    progress: int
