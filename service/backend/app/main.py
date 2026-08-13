from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .inference import extract, get_pipeline, render_graph_html
from .schemas import ExtractRequest, ExtractResponse, GraphHtmlRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_pipeline()
    yield


app = FastAPI(
    title="Temporal Graph Extraction API",
    description="Извлекает события, участников и временные метки из текста и строит граф связей",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse)
def extract_endpoint(req: ExtractRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Текст не должен быть пустым")
    return extract(req.text, use_summary=req.use_summary)


@app.post("/graph/html", response_class=HTMLResponse)
def graph_html_endpoint(req: GraphHtmlRequest):
    html = render_graph_html(
        [n.model_dump() for n in req.nodes],
        [e.model_dump() for e in req.edges],
    )
    return HTMLResponse(content=html)
