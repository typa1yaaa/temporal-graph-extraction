# Смоук-тесты на реальном пайплайне (суммаризатор + дообученная модель).
# Отключены по умолчанию, так как требуют скачивания весов и обученной
# модели извлечения событий (см. notebooks/rut5_trainer.ipynb и
# HF_MODEL_REPO_ID в src/graph_extraction/config.py). Раскомментируйте
# после того как модель будет обучена и опубликована / доступна локально.

# import pytest

# from src.graph_extraction.pipeline import TemporalGraphPipeline


# @pytest.fixture(scope="session")
# def pipeline():
#     return TemporalGraphPipeline()


# @pytest.mark.slow
# def test_models_load_without_error(pipeline):
#     assert pipeline.summarizer.model is not None
#     assert pipeline.event_model.model is not None


# @pytest.mark.slow
# def test_pipeline_extracts_events_from_causal_text(pipeline):
#     text = (
#         "Завод снизил выбросы, так как фильтры обновили. "
#         "Экологи зафиксировали улучшение показателей на следующий год."
#     )

#     result = pipeline.run(text, use_summary=False)

#     assert len(result["nodes"]) > 0, f"Ожидались события, получено: {result}"


# @pytest.mark.slow
# def test_empty_text_returns_empty_result(pipeline):
#     result = pipeline.run("", use_summary=True)

#     assert result == {"summary": None, "nodes": [], "edges": []}


# @pytest.mark.slow
# def test_pipeline_result_has_expected_shape(pipeline):
#     text = "Компания вышла на новый рынок в 2023 году, инвесторы поддержали расширение."

#     result = pipeline.run(text, use_summary=True)

#     assert set(result.keys()) == {"summary", "nodes", "edges"}
#     for node in result["nodes"]:
#         assert set(node.keys()) == {"id", "date", "person", "text"}
#     for edge in result["edges"]:
#         assert set(edge.keys()) == {"source", "target", "type"}
