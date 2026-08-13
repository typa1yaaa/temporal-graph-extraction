from dataclasses import dataclass, field


DEFAULT_DATE = "Не указана"
DEFAULT_PERSON = "Не указан"


@dataclass
class Node:
    id: str
    date: str = DEFAULT_DATE
    person: str = DEFAULT_PERSON
    text: str = ""

    def to_dict(self) -> dict:
        return {"id": self.id, "date": self.date, "person": self.person, "text": self.text}


@dataclass
class Edge:
    source: str
    target: str
    type: str

    def to_dict(self) -> dict:
        return {"source": self.source, "target": self.target, "type": self.type}


@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
