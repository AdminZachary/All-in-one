import os
from pathlib import Path
import git
import urllib.request
from huggingface_hub import hf_hub_download
from backend.utils.logger import boot_logger
from backend.utils.config import DATA_DIR

MODELS_DIR = DATA_DIR / "models"
REPOS_DIR = DATA_DIR / "repos"

def download_mock_models():
    """
    Prepares the offline environment.
    For Wan2GP, we now clone the actual native repository.
    For InfiniteTalk, we continue to use a mock download until its heavy CUDA env is ready.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    REPOS_DIR.mkdir(parents=True, exist_ok=True)
    
    boot_logger.info("Wan2GP source is now embedded natively. Skipping runtime clone.")

    # 2. Mock InfiniteTalk
    repo_id = "bert-base-uncased"
    filename = "config.json"
    infinitetalk_model_path = MODELS_DIR / "infinitetalk_mock.json"
    
    if not infinitetalk_model_path.exists():
        boot_logger.info("Downloading InfiniteTalk offline model weights ...")
        downloaded_path = hf_hub_download(repo_id=repo_id, filename=filename)
        with open(downloaded_path, 'rb') as src, open(infinitetalk_model_path, 'wb') as dst:
            dst.write(src.read())
        boot_logger.info(f"InfiniteTalk model saved to {infinitetalk_model_path}")
    else:
        boot_logger.info("InfiniteTalk model already exists offline.")

    # 3. Sample valid MP4 for Frontend Video Player verification
    sample_mp4 = MODELS_DIR / "sample.mp4"
    if not sample_mp4.exists():
        boot_logger.info("Downloading a valid sample MP4 for frontend testing...")
        try:
            url = "https://raw.githubusercontent.com/mdn/learning-area/master/html/multimedia-and-embedding/video-and-audio-content/rabbit320.mp4"
            urllib.request.urlretrieve(url, sample_mp4)
            boot_logger.info("Sample MP4 downloaded.")
        except Exception as e:
            boot_logger.error(f"Failed to download sample mp4: {e}")

if __name__ == "__main__":
    download_mock_models()
