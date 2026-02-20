import asyncio
import traceback
from backend.storage.db import update_job_status
from backend.engines.wan2gp_adapter import Wan2GPAdapter
from backend.engines.infinitetalk_adapter import InfiniteTalkAdapter
from backend.utils.logger import worker_logger

WAN2GP_ENGINE = Wan2GPAdapter()
INFINITETALK_ENGINE = InfiniteTalkAdapter()

class JobService:
    @staticmethod
    def _get_engine(engine_name: str):
        if engine_name == "infinitetalk":
            return INFINITETALK_ENGINE
        return WAN2GP_ENGINE

    @staticmethod
    async def _update_progress_loop(job_id: str):
        """Simulates detailed progress steps."""
        progress = 10
        stages = [
            (30, "音频预处理..."),
            (50, "口型驱动..."),
            (70, "面部光影重绘..."),
            (90, "渲染帧..."),
        ]
        
        try:
            for next_prog, msg in stages:
                await asyncio.sleep(0.8)
                update_job_status(job_id, {"progress": next_prog, "message": msg})
        except asyncio.CancelledError:
            pass # Routine cancellation is fine

    @staticmethod
    async def process_job_async(job_id: str, voice_id: str, avatar_url: str, script_text: str, preferred_engine: str):
        """The main orchestration function running in the background."""
        worker_logger.info(f"Worker picked up job {job_id} requesting engine '{preferred_engine}'")
        update_job_status(job_id, {"status": "running", "message": "解析空间特征...", "progress": 10})
        
        progress_task = asyncio.create_task(JobService._update_progress_loop(job_id))

        try:
            primary_engine = JobService._get_engine(preferred_engine)
            selected_engine = primary_engine.name
            update_job_status(job_id, {"selected_engine": selected_engine})
            
            try:
                 # Attempt processing with the primary engine
                 result_url = await primary_engine.process_job(job_id, voice_id, avatar_url, script_text)
            except Exception as e:
                # Fallback Strategy: If infinitetalk fails, fallback to wan2gp natively.
                if selected_engine == "infinitetalk":
                    worker_logger.warning(f"Engine {selected_engine} failed for {job_id}. Reason: {e}. Falling back to wan2gp.")
                    
                    selected_engine = "wan2gp"
                    err_msg = str(e)
                    
                    update_job_status(job_id, {
                        "selected_engine": selected_engine, 
                        "fallback_reason": err_msg,
                        "message": "引擎回退中：正在切换到兼容模式..."
                    })
                    
                    fallback_engine = JobService._get_engine("wan2gp")
                    result_url = await fallback_engine.process_job(job_id, voice_id, avatar_url, script_text)
                else:
                    raise e # No fallback available for wan2gp failure

            # Success Path
            if not progress_task.done():
                progress_task.cancel()
            update_job_status(job_id, {
                "status": "completed",
                "progress": 100,
                "message": "完成",
                "result_url": result_url
            })
            worker_logger.info(f"Job {job_id} successfully finalized using {selected_engine}.")
            
        except Exception as failed_err:
            if not progress_task.done():
                progress_task.cancel()
            err_trace = traceback.format_exc()
            worker_logger.error(f"Job {job_id} failed permanently.\n{err_trace}")
            update_job_status(job_id, {
                "status": "failed",
                "message": f"遭遇致命错误: {str(failed_err)}"
            })
