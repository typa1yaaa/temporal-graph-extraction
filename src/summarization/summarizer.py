from typing import Optional

import torch
from transformers import AutoTokenizer, T5ForConditionalGeneration

from .. import config


class Summarizer:
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        model_name = model_name or config.SUMMARIZER_MODEL_NAME

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

    @torch.no_grad()
    def summarize(
        self,
        text: str,
        max_input_length: int = config.SUMMARY_MAX_INPUT_LENGTH,
        max_output_length: int = config.SUMMARY_MAX_OUTPUT_LENGTH,
    ) -> str:
        if not text or not text.strip():
            return ""

        inputs = self.tokenizer(
            [text], max_length=max_input_length, truncation=True, return_tensors="pt"
        ).to(self.device)

        output_ids = self.model.generate(
            **inputs, no_repeat_ngram_size=4, num_beams=5, max_length=max_output_length
        )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
