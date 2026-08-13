from functools import lru_cache
from typing import Optional

from src import config
from .graph.builder import build_graph
from .graph_extraction.model import EventExtractionModel
from .graph_extraction.parser import parse_event_output
from .summarization.summarizer import Summarizer


class TemporalGraphPipeline:
    def __init__(
        self,
        summarizer: Optional[Summarizer] = None,
        event_model: Optional[EventExtractionModel] = None,
    ):
        self._summarizer = summarizer
        self._event_model = event_model

    @property
    def summarizer(self) -> Summarizer:
        if self._summarizer is None:
            self._summarizer = Summarizer()
        return self._summarizer

    @property
    def event_model(self) -> EventExtractionModel:
        if self._event_model is None:
            self._event_model = EventExtractionModel()
        return self._event_model

    def run(self, text: str, use_summary: bool = True) -> dict:
        if not text or not text.strip():
            return {"summary": None, "nodes": [], "edges": []}

        if use_summary:
            processed_text = self.summarizer.summarize(text)
        else:
            processed_text = text[: config.MAX_RAW_TEXT_LENGTH]

        raw_output = self.event_model.generate(processed_text)
        vertices, edges = parse_event_output(raw_output)
        graph = build_graph(vertices, edges)

        return {
            "summary": processed_text if use_summary else None,
            "nodes": [n.to_dict() for n in graph.nodes],
            "edges": [e.to_dict() for e in graph.edges],
        }


@lru_cache
def get_pipeline() -> TemporalGraphPipeline:
    return TemporalGraphPipeline()
