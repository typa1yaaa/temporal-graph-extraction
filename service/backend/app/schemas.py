from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10_000)
    use_summary: bool = True


class NodeSchema(BaseModel):
    id: str
    date: str
    person: str
    text: str


class EdgeSchema(BaseModel):
    source: str
    target: str
    type: str


class ExtractResponse(BaseModel):
    summary: str | None
    nodes: list[NodeSchema]
    edges: list[EdgeSchema]


class GraphHtmlRequest(BaseModel):
    nodes: list[NodeSchema]
    edges: list[EdgeSchema]
