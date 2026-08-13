from functools import lru_cache

from src.graph.builder import build_pyvis_html
from src.graph.types import Edge, Graph, Node
from src.pipeline import TemporalGraphPipeline


@lru_cache
def get_pipeline() -> TemporalGraphPipeline:
    return TemporalGraphPipeline()


def extract(text: str, use_summary: bool = True) -> dict:
    pipeline = get_pipeline()
    return pipeline.run(text, use_summary=use_summary)


def render_graph_html(nodes: list[dict], edges: list[dict]) -> str:
    graph = Graph(
        nodes=[Node(**n) for n in nodes],
        edges=[Edge(**e) for e in edges],
    )
    return build_pyvis_html(graph)
