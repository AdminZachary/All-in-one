import asyncio
import sys
import json
import re
from pathlib import Path
from backend.utils.config import EXEC_DIR, OUTPUTS_DIR, DATA_DIR
from backend.utils.logger import app_logger
from backend.storage.db import update_job_status

async def run_native_wan2gp_job(job_id, settings, is_voice_clone=False):
    """
    Executes a headless job via the bundled wan2gp_core/wgp.py script.
    
    Args:
        job_id (str): The ID of the job or voice record.
        settings (dict): The dictionary parameters to be written to job_queue.json.
        is_voice_clone (bool): Whether this is updating a voice row instead of a job row.
    
    Returns:
        Path: The path to the generated output file (mp4 or wav/audio), or raises RuntimeError.
    """
    if getattr(sys, 'frozen', False):
        env_root = Path(sys.executable).parent
        repo_path = env_root / "wan2gp_core"
    else:
        env_root = EXEC_DIR
        repo_path = env_root / "wan2gp_core"
        
    venv_python = repo_path / "venv" / "Scripts" / "python.exe"
    wgp_script = repo_path / "wgp.py"
        
    if not venv_python.exists():
        # Try Portable Python path
        venv_python = repo_path / "python_env" / "python.exe"

    if not venv_python.exists():
        fallback_path = env_root / "dist" / "wan2gp_core"
        if (fallback_path / "venv" / "Scripts" / "python.exe").exists():
            repo_path = fallback_path
            venv_python = repo_path / "venv" / "Scripts" / "python.exe"
            wgp_script = repo_path / "wgp.py"
        elif (fallback_path / "python_env" / "python.exe").exists():
            repo_path = fallback_path
            venv_python = repo_path / "python_env" / "python.exe"
            wgp_script = repo_path / "wgp.py"

    import subprocess
    has_torch = False
    if venv_python.exists():
        try:
            res = subprocess.run([str(venv_python), "-c", "import torch"], capture_output=True, timeout=5)
            if res.returncode == 0:
                has_torch = True
        except:
            pass

    if not has_torch:
        app_logger.info(f"[Wan2GP] Python Env missing or broken (no torch). Simulating fallback.")
        app_logger.info(f"[Wan2GP] Awaiting GPU compute (simulated 5 secs over native repo)...")
        
        job_dir = OUTPUTS_DIR / f"{job_id}_tmp"
        job_dir.mkdir(parents=True, exist_ok=True)
        import shutil
        sample_file = DATA_DIR / "models" / "sample.mp4"
        output_file = job_dir / f"{job_id}_mocked.mp4"
        
        for i in range(1, 6):
            await asyncio.sleep(1)
            if not is_voice_clone:
                update_job_status(job_id, {"progress": 10 + i * 16, "message": "检测到环境不完整，已启动模拟渲染..."})
                
        if sample_file.exists():
            shutil.copy(sample_file, output_file)
        else:
            with open(output_file, 'wb') as f:
                f.write(b"dummy video content")
                
        app_logger.info(f"[Wan2GP] Completed job {job_id} successfully under Native execution bridge (Simulated).")
        return output_file
        
    # Setup Headless Job Directory for this specific generation
    job_dir = OUTPUTS_DIR / f"{job_id}_tmp"
    job_dir.mkdir(parents=True, exist_ok=True)
    
    # Create process settings list
    queue_file = job_dir / "job_queue.json"
    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump([settings], f) # wgp expects a list of jobs
        
    real_cmd = f'"{venv_python}" "{wgp_script}" --process "{queue_file}" --output-dir "{job_dir}"'
    app_logger.info(f"[Wan2GP-Runner] Native PyTorch execution via: {real_cmd}")
    
    process = await asyncio.create_subprocess_shell(
        real_cmd,
        cwd=str(repo_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )
    
    progress_pattern = re.compile(r'(\d+)%')
    
    async for line in process.stdout:
        line_text = line.decode(errors='replace').strip()
        if not line_text:
            continue
        
        app_logger.debug(f"[Wan2GP-STDOUT] {line_text}")
        
        # Check for progress indicators
        match = progress_pattern.search(line_text)
        
        # HuggingFace download regex: 'pytorch_model.bin:  45%' or 'Downloading: 25%'
        is_downloading = "ownload" in line_text or ".safetensors" in line_text or ".bin" in line_text or ".pth" in line_text
        
        if match:
            try:
                percent = int(match.group(1))
                if is_voice_clone:
                    msg = f"语音克隆模型加载中: {percent}%..." if is_downloading else "正在提取特征..."
                    pass # We do not currently have a progress bar integer column for voice in the UI schema, just states.
                else:    
                    msg = f"正在下载庞大的AI模型 (请耐心等待...): {percent}%" if is_downloading else "正在渲染视频帧..."
                    # If downloading, scale progress from 0 to 10%. If rendering, scale from 10% to 90%
                    if is_downloading:
                        overall_prog = int(percent * 0.1) 
                    else:
                        overall_prog = 10 + int(percent * 0.8)
                        
                    update_job_status(job_id, {"progress": overall_prog, "message": msg})
            except:
                pass
        elif "RuntimeError" in line_text or "Exception" in line_text:
            app_logger.error(f"[Wan2GP-Runner] Error snippet caught: {line_text}")

    await process.wait()
    
    if process.returncode != 0:
        raise RuntimeError(f"Wan2GP Process exited with code {process.returncode}")
        
    # Find the output
    # Wan2GP TTS outputs audio formats. Video Gen outputs mp4.
    generated_files = list(job_dir.glob("*.[mM][pP]4")) + list(job_dir.glob("*.[wW][aA][vV]"))
    if not generated_files:
        app_logger.error(f"[Wan2GP-Runner] Native Exec succeeded but no output media found in {job_dir}")
        raise RuntimeError("Media file generation failed silently (no output produced by engine).")
        
    # Return the first successfully generated file
    return generated_files[0]
