import networkx as nx
from pyvis.network import Network

from .types import Edge, Graph, Node

EDGE_COLORS = {
    "temporal": "blue",
    "causal": "red",
    "causes": "orange",
    "enables": "green",
    "flashback": "purple",
    "leads to": "green",
}
DEFAULT_EDGE_COLOR = "gray"


def build_graph(vertices: dict[str, Node], edges: list[Edge]) -> Graph:
    node_list = list(vertices.values())
    valid_edges = [e for e in edges if e.source in vertices and e.target in vertices]
    return Graph(nodes=node_list, edges=valid_edges)


def to_networkx(graph: Graph) -> nx.DiGraph:
    g = nx.DiGraph()
    for node in graph.nodes:
        hover_text = f"Событие: {node.text}\nУчастник: {node.person}\nДата: {node.date}"
        g.add_node(node.id, label=node.id, title=hover_text)

    for edge in graph.edges:
        color = EDGE_COLORS.get(edge.type, DEFAULT_EDGE_COLOR)
        g.add_edge(edge.source, edge.target, label=edge.type, title=edge.type, color=color)

    return g


def build_pyvis_html(graph: Graph) -> str:
    nx_graph = to_networkx(graph)

    net = Network(height="900px", width="100%", directed=True, bgcolor="#1E1E1E", font_color="white")
    net.from_nx(nx_graph)
    net.set_options(
        """
        var options = {
          "physics": {"enabled": true, "stabilization": true},
          "edges": {"arrows": {"to": true}, "font": {"size": 12}},
          "nodes": {"font": {"size": 20, "face": "arial"}, "shape": "circle", "size": 30},
          "interaction": {"zoomView": true, "dragView": true}
        }
        """
    )
    return net.generate_html()
