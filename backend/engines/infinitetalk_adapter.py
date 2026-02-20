import asyncio
import os
import random
import subprocess
from pathlib import Path
from backend.engines.base import BaseEngineAdapter
from backend.utils.logger import app_logger
from backend.utils.config import OUTPUTS_DIR, DATA_DIR

class InfiniteTalkAdapter(BaseEngineAdapter):
    @property
    def name(self) -> str:
        return "infinitetalk"

    async def process_job(self, job_id, voice_id, avatar_url, script_text) -> str:
        app_logger.info(f"[InfiniteTalk] Starting generation for job {job_id}")
        
        # Verify the model exists
        model_path = DATA_DIR / "models" / "infinitetalk_mock.json"
        if not model_path.exists():
             raise RuntimeError("InfiniteTalk local offline model not found! Please restart app to trigger download.")

        # In a real scenario, this runs MeiGen-AI/InfiniteTalk:
        # subprocess.run(["python", "-m", "infinitetalk.inference", "--weights", str(model_path)])
        
        # We simulate a 50% failure rate (CUDA OOM, memory error) to demonstrate the fallback mechanism to Wan2GP.
        if random.random() < 0.5:
            # We purposely simulate a process crash
            app_logger.warning(f"[InfiniteTalk] Subprocess simulated failure for job {job_id} to trigger fallback.")
            raise RuntimeError("InfiniteTalk engine subprocess encountered a VRAM OOM error or timeout.")
            
        output_file = OUTPUTS_DIR / f"{job_id}_infinitetalk.mp4"
        create_mp4_cmd = f"python -c \"import time; time.sleep(5); open('{output_file.as_posix()}', 'w').write('mock infinitetalk video content')\""

        process = await asyncio.create_subprocess_shell(
            create_mp4_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            app_logger.error(f"[InfiniteTalk] Subprocess failed: {stderr.decode()}")
            raise RuntimeError(f"InfiniteTalk Process Error: {stderr.decode()}")
            
        app_logger.info(f"[InfiniteTalk] Completed job {job_id} successfully")
        return f"/data/outputs/{job_id}_infinitetalk.mp4"
