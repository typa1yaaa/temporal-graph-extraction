from huggingface_hub import snapshot_download

from ... import config

if __name__ == "__main__":
    print(f"Downloading event extraction model: {config.HF_MODEL_REPO_ID}")
    path = snapshot_download(repo_id=config.HF_MODEL_REPO_ID)
    print(f"MODEL DOWNLOAD COMPLETE: {path}")

    print(f"Downloading summarizer model: {config.SUMMARIZER_MODEL_NAME}")
    path = snapshot_download(repo_id=config.SUMMARIZER_MODEL_NAME)
    print(f"MODEL DOWNLOAD COMPLETE: {path}")
