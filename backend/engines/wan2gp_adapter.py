import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from backend.engines.base import BaseEngineAdapter
from backend.utils.logger import app_logger
from backend.utils.config import OUTPUTS_DIR, DATA_DIR

class Wan2GPAdapter(BaseEngineAdapter):
    @property
    def name(self) -> str:
        return "wan2gp"

    async def process_job(self, job_id, voice_id, avatar_url, script_text, wangp_model="Wan t2v 1.3B") -> str:
        app_logger.info(f"[Wan2GP] Starting generation for job {job_id}")
        
        # 1. Verify Native Repo Exists
        import sys
        if getattr(sys, 'frozen', False):
            # When frozen as All-in-one_backend.exe, it sits in dist/
            env_root = Path(sys.executable).parent
            repo_path = env_root / "wan2gp_core"
        else:
            # During dev mode
            env_root = Path(__file__).resolve().parent.parent.parent
            repo_path = env_root / "wan2gp_core"
            
        if not repo_path.exists():
            fallback_path = env_root / "dist" / "wan2gp_core"
            if fallback_path.exists():
                repo_path = fallback_path
            else:
                raise RuntimeError(f"Native Wan2GP source not found at {repo_path}. Ensure it is bundled.")

        output_file = OUTPUTS_DIR / f"{job_id}_wan2gp.mp4"
        sample_mp4 = DATA_DIR / "models" / "sample.mp4"
        
        # Use our centralized native executor wrapper
        from backend.utils.wan2gp_runner import run_native_wan2gp_job
        
        # Mapping frontend selection to actual Native WanGP models
        frontend_model = wangp_model
        model_type = "t2v_1.3B" # default fallback
        is_avatar = False
        
        if "Hunyuan Avatar" in frontend_model:
            model_type = "hunyuan_avatar"
            is_avatar = True
        elif "Multitalk" in frontend_model:
            model_type = "multitalk"
            is_avatar = True
        elif "Fantasy" in frontend_model:
            model_type = "fantasy"
            is_avatar = True
        elif "14B" in frontend_model:
            model_type = "t2v"
            
        settings = {
            "id": 1,
            "params": {
                "model_type": model_type,
                "prompt": script_text,
                "resolution": "480x832", # Portrait is good for humans
            }
        }
        
        # Inject custom avatar prompts if this is an Avatar model
        if is_avatar:
            audio_path = voice_id
            img_path = avatar_url
            import urllib.request
            import tempfile
            from urllib.parse import urlparse

            if img_path:
                if img_path.startswith("http://") or img_path.startswith("https://"):
                    app_logger.info(f"[Wan2GP] Downloading avatar image from {img_path}")
                    try:
                        parsed_url = urlparse(img_path)
                        ext = os.path.splitext(parsed_url.path)[1]
                        if not ext:
                            ext = ".jpg"
                        tmp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir=OUTPUTS_DIR)
                        urllib.request.urlretrieve(img_path, tmp_img_file.name)
                        tmp_img_file.close()
                        img_path = tmp_img_file.name
                        app_logger.info(f"[Wan2GP] Downloaded avatar to {img_path}")
                    except Exception as e:
                        app_logger.error(f"[Wan2GP] Failed to download avatar image: {e}")
                        # Will pass original path, likely failing later
                
                settings["params"]["image_start"] = img_path
                settings["params"]["image_prompt_type"] = "I" # Reference Image
            
            app_logger.info(f"[Wan2GP] Avatar Mode active. Audio Guide: {audio_path}")
            
        try:
            generated_file = await run_native_wan2gp_job(job_id, settings, is_voice_clone=False)
            
            # Copy to final destination
            import shutil
            shutil.copy(generated_file, output_file)
            
            # Clean up temp folder
            try:
                shutil.rmtree(generated_file.parent)
            except:
                pass
                
            app_logger.info(f"[Wan2GP] Native inference generated successfully at {output_file}")
            return f"/api/jobs/{job_id}/result"
        except Exception as e:
            app_logger.error(f"[Wan2GP] Native Exec failed: {str(e)}")
            raise e
