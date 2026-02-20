import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from backend.utils.logger import boot_logger
from backend.utils.config import DATA_DIR

MODELS_DIR = DATA_DIR / "models"

def download_mock_models():
    """
    Downloads lightweight surrogate models/scripts to simulate the presence
    of Wan2GP and InfiniteTalk offline weights.
    In a real scenario, this would fetch the actual GB-sized safetensors.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    # We will use a tiny public file from huggingface as a "mock weight" just to prove the downloader works.
    # For instance, a small config file or tokenizer from a popular repo.
    repo_id = "bert-base-uncased"
    filename = "config.json"
    
    wan2gp_model_path = MODELS_DIR / "wan2gp_mock.json"
    infinitetalk_model_path = MODELS_DIR / "infinitetalk_mock.json"
    
    if not wan2gp_model_path.exists():
        boot_logger.info("Downloading Wan2GP offline model weights ...")
        downloaded_path = hf_hub_download(repo_id=repo_id, filename=filename)
        # Copy to our models dir
        with open(downloaded_path, 'rb') as src, open(wan2gp_model_path, 'wb') as dst:
            dst.write(src.read())
        boot_logger.info(f"Wan2GP model saved to {wan2gp_model_path}")
    else:
        boot_logger.info("Wan2GP model already exists offline.")

    if not infinitetalk_model_path.exists():
        boot_logger.info("Downloading InfiniteTalk offline model weights ...")
        downloaded_path = hf_hub_download(repo_id=repo_id, filename=filename)
        with open(downloaded_path, 'rb') as src, open(infinitetalk_model_path, 'wb') as dst:
            dst.write(src.read())
        boot_logger.info(f"InfiniteTalk model saved to {infinitetalk_model_path}")
    else:
        boot_logger.info("InfiniteTalk model already exists offline.")

if __name__ == "__main__":
    download_mock_models()
