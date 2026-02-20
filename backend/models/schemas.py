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

class CreateJobResponse(BaseModel):
    job_id: str
    selected_engine: Literal["wan2gp", "infinitetalk"]

class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    progress: int
    message: str
    selected_engine: str
    fallback_reason: str | None = None
    generated_script: str | None = None
    result_url: str | None = None
