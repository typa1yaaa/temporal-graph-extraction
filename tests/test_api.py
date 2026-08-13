import pytest
from fastapi.testclient import TestClient

from service.backend.app import inference, main


class FakePipeline:
    def run(self, text, use_summary=True):
        return {
            "summary": "сжатый текст" if use_summary else None,
            "nodes": [{"id": "V1", "date": "2020", "person": "Не указан", "text": "событие"}],
            "edges": [],
        }


@pytest.fixture
def client(monkeypatch):
    fake_pipeline = FakePipeline()
    monkeypatch.setattr(inference, "get_pipeline", lambda: fake_pipeline)
    monkeypatch.setattr(main, "get_pipeline", lambda: fake_pipeline)
    return TestClient(main.app)


def test_health_endpoint_returns_ok(client):
    resp = client.get("/health")

    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_extract_endpoint_returns_nodes_and_edges(client):
    resp = client.post("/extract", json={"text": "какой-то текст", "use_summary": True})

    assert resp.status_code == 200
    data = resp.json()
    assert data["summary"] == "сжатый текст"
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["id"] == "V1"


def test_extract_endpoint_without_summary(client):
    resp = client.post("/extract", json={"text": "какой-то текст", "use_summary": False})

    assert resp.status_code == 200
    assert resp.json()["summary"] is None


def test_extract_endpoint_rejects_empty_text(client):
    resp = client.post("/extract", json={"text": "   ", "use_summary": True})

    assert resp.status_code in (400, 422)


def test_extract_endpoint_rejects_missing_text_field(client):
    resp = client.post("/extract", json={"use_summary": True})

    assert resp.status_code == 422


def test_graph_html_endpoint_returns_html(client):
    resp = client.post(
        "/graph/html",
        json={
            "nodes": [{"id": "V1", "date": "2020", "person": "Не указан", "text": "событие"}],
            "edges": [],
        },
    )

    assert resp.status_code == 200
    assert "<html" in resp.text.lower()


def test_graph_html_endpoint_handles_empty_graph(client):
    resp = client.post("/graph/html", json={"nodes": [], "edges": []})

    assert resp.status_code == 200
