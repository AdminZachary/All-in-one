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

    async def process_job(self, job_id, voice_id, avatar_url, script_text, wangp_model="Wan t2v 1.3B") -> str:
        app_logger.info(f"[InfiniteTalk] Starting generation for job {job_id}")
        
        # Verify the model exists
        model_path = DATA_DIR / "models" / "infinitetalk_mock.json"
        if not model_path.exists():
             raise RuntimeError("InfiniteTalk local offline model not found! Please restart app to trigger download.")

        # In a real scenario, this runs MeiGen-AI/InfiniteTalk:
        # subprocess.run(["python", "-m", "infinitetalk.inference", "--weights", str(model_path)])
        
        # As per user request, we remove all "mock" generation.
        # Since the true InfiniteTalk repository isn't bundled (tens of GBs), this will always fail and fallback.
        app_logger.error(f"[InfiniteTalk] Native Engine block missing. Falling back.")
        raise RuntimeError("InfiniteTalk 原生推理引擎未安装，自动回退到默认引擎。")
            
        app_logger.info(f"[InfiniteTalk] Completed job {job_id} successfully")
        return f"/data/outputs/{job_id}_infinitetalk.mp4"
