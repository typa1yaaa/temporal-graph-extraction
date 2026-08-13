from src.graph.types import Edge, Graph, Node


def test_node_to_dict_contains_all_fields():
    node = Node(id="V1", date="2020", person="Анна", text="событие")

    assert node.to_dict() == {"id": "V1", "date": "2020", "person": "Анна", "text": "событие"}


def test_node_has_sensible_defaults():
    node = Node(id="V1")

    assert node.date == "Не указана"
    assert node.person == "Не указан"
    assert node.text == ""


def test_edge_to_dict_contains_all_fields():
    edge = Edge(source="V1", target="V2", type="causes")

    assert edge.to_dict() == {"source": "V1", "target": "V2", "type": "causes"}


def test_graph_to_dict_serializes_nodes_and_edges():
    graph = Graph(
        nodes=[Node(id="V1"), Node(id="V2")],
        edges=[Edge(source="V1", target="V2", type="causes")],
    )

    data = graph.to_dict()

    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["edges"][0]["type"] == "causes"


def test_empty_graph_has_empty_lists_by_default():
    graph = Graph()

    assert graph.nodes == []
    assert graph.edges == []


def test_two_graph_instances_do_not_share_default_lists():
    # dataclass с изменяемым значением по умолчанию — классическая ловушка;
    # проверяем, что используется field(default_factory=...), а не общий список.
    graph_a = Graph()
    graph_b = Graph()

    graph_a.nodes.append(Node(id="V1"))

    assert graph_b.nodes == []
