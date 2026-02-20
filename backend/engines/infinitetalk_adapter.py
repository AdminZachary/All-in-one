import asyncio
import random
from backend.engines.base import BaseEngineAdapter
from backend.utils.logger import app_logger

class InfiniteTalkAdapter(BaseEngineAdapter):
    @property
    def name(self) -> str:
        return "infinitetalk"

    async def process_job(self, job_id, voice_id, avatar_url, script_text) -> str:
        app_logger.info(f"[InfiniteTalk] Starting generation for job {job_id}")
        
        # Simulate initial setup time
        await asyncio.sleep(1.0)
        
        # We simulate a 50% failure rate to demonstrate the fallback mechanism to Wan2GP.
        # In the future, this integrates with MeiGen-AI/InfiniteTalk.
        if random.random() < 0.5:
            app_logger.warning(f"[InfiniteTalk] Simulated failure for job {job_id} to trigger fallback.")
            raise RuntimeError("InfiniteTalk engine encountered a VRAM OOM error or timeout.")

        # Simulate successful processing time
        await asyncio.sleep(3.0)
        
        app_logger.info(f"[InfiniteTalk] Completed job {job_id} successfully")
        return f"/data/outputs/{job_id}_infinitetalk.mp4"
