from src.graph.builder import build_graph, build_pyvis_html, to_networkx
from src.graph.types import Edge, Node


def test_build_graph_keeps_all_provided_vertices():
    vertices = {"V1": Node(id="V1"), "V2": Node(id="V2")}
    edges = [Edge(source="V1", target="V2", type="causes")]

    graph = build_graph(vertices, edges)

    assert {n.id for n in graph.nodes} == {"V1", "V2"}
    assert len(graph.edges) == 1


def test_build_graph_drops_edges_with_unknown_endpoints():
    vertices = {"V1": Node(id="V1")}
    edges = [
        Edge(source="V1", target="V2", type="causes"),  # V2 не существует
        Edge(source="V3", target="V1", type="temporal"),  # V3 не существует
    ]

    graph = build_graph(vertices, edges)

    assert graph.edges == []


def test_build_graph_with_no_edges_produces_isolated_nodes():
    vertices = {"V1": Node(id="V1"), "V2": Node(id="V2")}

    graph = build_graph(vertices, [])

    assert len(graph.nodes) == 2
    assert graph.edges == []


def test_to_networkx_creates_matching_nodes_and_edges():
    vertices = {"V1": Node(id="V1", text="a"), "V2": Node(id="V2", text="b")}
    edges = [Edge(source="V1", target="V2", type="causes")]
    graph = build_graph(vertices, edges)

    nx_graph = to_networkx(graph)

    assert set(nx_graph.nodes) == {"V1", "V2"}
    assert nx_graph.has_edge("V1", "V2")
    assert nx_graph.edges["V1", "V2"]["color"] == "orange"


def test_to_networkx_uses_default_color_for_unknown_edge_type():
    vertices = {"V1": Node(id="V1"), "V2": Node(id="V2")}
    edges = [Edge(source="V1", target="V2", type="mystery_type")]
    graph = build_graph(vertices, edges)

    nx_graph = to_networkx(graph)

    assert nx_graph.edges["V1", "V2"]["color"] == "gray"


def test_build_pyvis_html_returns_non_empty_html_string():
    vertices = {"V1": Node(id="V1", text="событие"), "V2": Node(id="V2", text="другое")}
    edges = [Edge(source="V1", target="V2", type="causes")]
    graph = build_graph(vertices, edges)

    html = build_pyvis_html(graph)

    assert isinstance(html, str)
    assert "<html" in html.lower()


def test_build_pyvis_html_handles_empty_graph_without_error():
    html = build_pyvis_html(build_graph({}, []))

    assert isinstance(html, str)
    assert "<html" in html.lower()
