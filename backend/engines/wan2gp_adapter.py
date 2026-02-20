import asyncio
import os
import subprocess
from pathlib import Path
from backend.engines.base import BaseEngineAdapter
from backend.utils.logger import app_logger
from backend.utils.config import OUTPUTS_DIR, DATA_DIR

class Wan2GPAdapter(BaseEngineAdapter):
    @property
    def name(self) -> str:
        return "wan2gp"

    async def process_job(self, job_id, voice_id, avatar_url, script_text) -> str:
        app_logger.info(f"[Wan2GP] Starting generation for job {job_id}")
        
        # Verify the model exists
        model_path = DATA_DIR / "models" / "wan2gp_mock.json"
        if not model_path.exists():
            raise RuntimeError("Wan2GP local offline model not found! Please restart app to trigger download.")

        # Simulate processing by spawning a real Python subprocess
        output_file = OUTPUTS_DIR / f"{job_id}_wan2gp.mp4"
        
        # In a real Wan2GP scenario, we would call:
        # subprocess.run(["python", "-m", "wan2gp.inference", "--model", str(model_path), "--out", str(output_file)])
        
        # For our MVP mock, we create a dummy mp4 (which is just a text file for proof of concept)
        create_mp4_cmd = f"python -c \"import time; time.sleep(4); open('{output_file.as_posix()}', 'w').write('mock wan2gp video content')\""
        
        process = await asyncio.create_subprocess_shell(
            create_mp4_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            app_logger.error(f"[Wan2GP] Subprocess failed: {stderr.decode()}")
            raise RuntimeError(f"Wan2GP Process Error: {stderr.decode()}")
        
        app_logger.info(f"[Wan2GP] Completed job {job_id} successfully")
        return f"/data/outputs/{job_id}_wan2gp.mp4"
