import os
from pathlib import Path


SUMMARIZER_MODEL_NAME = "IlyaGusev/rut5_base_sum_gazeta"

HF_MODEL_REPO_ID = "ksruasdh/temporal-causal-graph-extractor"

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = REPO_ROOT / "data" / "df_text2graph.jsonl"
MODEL_OUTPUT_DIR = REPO_ROOT / "models" / "rut5_event_model"


SUMMARY_MAX_INPUT_LENGTH = 600
SUMMARY_MAX_OUTPUT_LENGTH = 256
EVENT_MAX_LENGTH = 256


MAX_RAW_TEXT_LENGTH = 1024


def get_model_source() -> str:
    if os.getenv("MODEL_SOURCE", "hub") == "local":
        return str(MODEL_OUTPUT_DIR)
    return HF_MODEL_REPO_ID
