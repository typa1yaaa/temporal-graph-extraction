from src.graph_extraction.parser import parse_event_output


def test_empty_text_returns_no_vertices_and_no_edges():
    vertices, edges = parse_event_output("")

    assert vertices == {}
    assert edges == []


def test_whitespace_only_text_returns_no_vertices():
    vertices, edges = parse_event_output("   \n  ")

    assert vertices == {}
    assert edges == []


def test_parses_vertices_with_date_person_and_text():
    raw = (
        "vertex_list:\n"
        "v1: 2019 | Иван Иванов | иван иванов подписал приказ\n"
        "v2: - | - | приказ вступил в силу\n\n"
        "relationship_list:\n"
        "v2->v1 causes"
    )

    vertices, edges = parse_event_output(raw)

    assert set(vertices.keys()) == {"V1", "V2"}
    assert vertices["V1"].date == "2019"
    assert vertices["V1"].person == "Иван Иванов"
    assert vertices["V1"].text == "иван иванов подписал приказ"

    assert vertices["V2"].date == "Не указана"
    assert vertices["V2"].person == "Не указан"

    assert len(edges) == 1
    assert edges[0].source == "V2"
    assert edges[0].target == "V1"
    assert edges[0].type == "causes"


def test_extracts_year_from_free_form_date_string():
    raw = "vertex_list:\nv1: в 1998 году | - | событие произошло\n\nrelationship_list:\n"

    vertices, _ = parse_event_output(raw)

    assert vertices["V1"].date == "1998"


def test_date_without_year_is_kept_as_is():
    raw = "vertex_list:\nv1: вчера вечером | - | событие произошло\n\nrelationship_list:\n"

    vertices, _ = parse_event_output(raw)

    assert vertices["V1"].date == "вчера вечером"


def test_vertex_without_pipe_separator_is_treated_as_plain_text():
    raw = "vertex_list:\nv1: просто событие без разделителей\n\nrelationship_list:\n"

    vertices, _ = parse_event_output(raw)

    assert vertices["V1"].text == "просто событие без разделителей"
    assert vertices["V1"].person == "Не указан"
    assert vertices["V1"].date == "Не указана"


def test_missing_relationship_list_header_gives_no_edges():
    raw = "vertex_list:\nv1: - | - | одинокое событие"

    vertices, edges = parse_event_output(raw)

    assert len(vertices) == 1
    assert edges == []


def test_edge_endpoints_are_uppercased_and_type_lowercased():
    raw = (
        "vertex_list:\nv1: - | - | а\nv2: - | - | б\n\n"
        "relationship_list:\nV1->V2 TEMPORAL"
    )

    _, edges = parse_event_output(raw)

    assert edges[0].source == "V1"
    assert edges[0].target == "V2"
    assert edges[0].type == "temporal"


def test_malformed_relationship_line_is_ignored():
    raw = "vertex_list:\nv1: - | - | одно событие\n\nrelationship_list:\n(нет связей)"

    _, edges = parse_event_output(raw)

    assert edges == []


def test_multiple_edges_are_all_parsed():
    raw = (
        "vertex_list:\nv1: - | - | а\nv2: - | - | б\nv3: - | - | в\n\n"
        "relationship_list:\nv2->v1 causes\nv3->v2 temporal"
    )

    _, edges = parse_event_output(raw)

    assert len(edges) == 2
    assert (edges[0].source, edges[0].target, edges[0].type) == ("V2", "V1", "causes")
    assert (edges[1].source, edges[1].target, edges[1].type) == ("V3", "V2", "temporal")


def test_vertex_ids_are_matched_case_insensitively():
    raw = "vertex_list:\nV1: - | - | событие в верхнем регистре\n\nrelationship_list:\n"

    vertices, _ = parse_event_output(raw)

    assert "V1" in vertices
