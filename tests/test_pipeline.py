from src.pipeline import TemporalGraphPipeline


RAW_OUTPUT = (
    "vertex_list:\n"
    "v1: 2020 | - | событие первое\n"
    "v2: - | - | событие второе\n\n"
    "relationship_list:\n"
    "v2->v1 causes"
)


class FakeSummarizer:
    def __init__(self, summary="сжатый текст"):
        self.summary = summary
        self.calls: list[str] = []

    def summarize(self, text, **kwargs):
        self.calls.append(text)
        return self.summary


class FakeEventModel:
    def __init__(self, raw_output=RAW_OUTPUT):
        self.raw_output = raw_output
        self.calls: list[str] = []

    def generate(self, text, **kwargs):
        self.calls.append(text)
        return self.raw_output


def test_run_with_summary_calls_summarizer_and_event_model():
    summarizer = FakeSummarizer(summary="краткая версия")
    event_model = FakeEventModel()
    pipeline = TemporalGraphPipeline(summarizer=summarizer, event_model=event_model)

    result = pipeline.run("длинный исходный текст", use_summary=True)

    assert summarizer.calls == ["длинный исходный текст"]
    assert event_model.calls == ["краткая версия"]
    assert result["summary"] == "краткая версия"
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1


def test_run_without_summary_skips_summarizer_and_uses_raw_text():
    summarizer = FakeSummarizer()
    event_model = FakeEventModel()
    pipeline = TemporalGraphPipeline(summarizer=summarizer, event_model=event_model)

    result = pipeline.run("исходный текст", use_summary=False)

    assert summarizer.calls == []
    assert event_model.calls == ["исходный текст"]
    assert result["summary"] is None


def test_run_truncates_raw_text_when_summary_disabled():
    summarizer = FakeSummarizer()
    event_model = FakeEventModel()
    pipeline = TemporalGraphPipeline(summarizer=summarizer, event_model=event_model)

    long_text = "а" * 2000
    pipeline.run(long_text, use_summary=False)

    assert len(event_model.calls[0]) <= 1024


def test_run_with_empty_text_returns_empty_result_without_calling_models():
    summarizer = FakeSummarizer()
    event_model = FakeEventModel()
    pipeline = TemporalGraphPipeline(summarizer=summarizer, event_model=event_model)

    result = pipeline.run("   ", use_summary=True)

    assert result == {"summary": None, "nodes": [], "edges": []}
    assert summarizer.calls == []
    assert event_model.calls == []


def test_run_returns_json_serializable_nodes_and_edges():
    summarizer = FakeSummarizer()
    event_model = FakeEventModel()
    pipeline = TemporalGraphPipeline(summarizer=summarizer, event_model=event_model)

    result = pipeline.run("текст", use_summary=False)

    assert result["nodes"][0] == {
        "id": "V1",
        "date": "2020",
        "person": "Не указан",
        "text": "событие первое",
    }
    assert result["edges"][0] == {"source": "V2", "target": "V1", "type": "causes"}


def test_lazy_properties_instantiate_real_components_only_when_accessed(monkeypatch):
    created = {}

    class DummySummarizer:
        def __init__(self):
            created["summarizer"] = True

    class DummyEventModel:
        def __init__(self):
            created["event_model"] = True

    monkeypatch.setattr("src.pipeline.Summarizer", DummySummarizer)
    monkeypatch.setattr("src.pipeline.EventExtractionModel", DummyEventModel)

    pipeline = TemporalGraphPipeline()

    assert created == {}

    _ = pipeline.summarizer
    assert created == {"summarizer": True}

    _ = pipeline.event_model
    assert created == {"summarizer": True, "event_model": True}


def test_lazy_property_caches_instance_across_calls(monkeypatch):
    instances_created = []

    class DummySummarizer:
        def __init__(self):
            instances_created.append(self)

    monkeypatch.setattr("src.pipeline.Summarizer", DummySummarizer)

    pipeline = TemporalGraphPipeline()

    first = pipeline.summarizer
    second = pipeline.summarizer

    assert first is second
    assert len(instances_created) == 1
