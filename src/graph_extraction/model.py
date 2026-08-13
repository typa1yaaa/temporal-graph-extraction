from pathlib import Path
from typing import Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from src import config


class EventExtractionModel:


    def __init__(self, model_path: Optional[str | Path] = None, device: Optional[str] = None):
        model_path = model_path or config.get_model_source()

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    @torch.no_grad()
    def generate(self, text: str, max_length: int = config.EVENT_MAX_LENGTH) -> str:
        if not text or not text.strip():
            return ""

        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=max_length
        ).to(self.device)

        output_ids = self.model.generate(**inputs, max_length=max_length)
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
