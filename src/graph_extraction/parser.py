import re

from src.graph.types import DEFAULT_DATE, DEFAULT_PERSON, Edge, Node


#   vertex_list:
#   v1: 2019 | Иван Иванов | иван иванов подписал приказ
#   v2: - | - | приказ вступил в силу
#
#   relationship_list:
#   v2->v1 causes


RELATIONSHIP_HEADER_RE = re.compile(r"(?i)relationship[_\s]*list[:\s]*")
VERTEX_ID_RE = re.compile(r"(?i)(v\d+)\s*:")
EDGE_RE = re.compile(r"(v\d+)\s*->\s*(v\d+)\s+(\w+)", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(\d{4})\b")


def _parse_date(raw_date: str) -> str:
    if not raw_date or raw_date == "-":
        return DEFAULT_DATE
    match = YEAR_RE.search(raw_date)
    return match.group(1) if match else raw_date


def parse_event_output(text: str) -> tuple[dict[str, Node], list[Edge]]:
    vertices: dict[str, Node] = {}
    edges: list[Edge] = []

    if not text or not text.strip():
        return vertices, edges

    parts = RELATIONSHIP_HEADER_RE.split(text)
    vertex_block = parts[0] if parts else ""
    relation_block = parts[1] if len(parts) > 1 else ""

    vertex_parts = VERTEX_ID_RE.split(vertex_block)
    for i in range(1, len(vertex_parts), 2):
        raw_id = vertex_parts[i]
        vertex_id = f"V{re.sub(r'[^0-9]', '', raw_id)}"
        content = vertex_parts[i + 1].strip() if i + 1 < len(vertex_parts) else ""

        if not content or "relationship" in content.lower():
            continue

        if "|" in content:
            chunks = [c.strip() for c in content.split("|")]
            raw_date = chunks[0] if len(chunks) > 0 else "-"
            person = chunks[1] if len(chunks) > 1 else DEFAULT_PERSON
            event_text = chunks[2] if len(chunks) > 2 else " ".join(chunks[1:])
        else:
            raw_date = "-"
            person = DEFAULT_PERSON
            event_text = content

        vertices[vertex_id] = Node(
            id=vertex_id,
            date=_parse_date(raw_date),
            person=person if person != "-" else DEFAULT_PERSON,
            text=event_text,
        )

    for match in EDGE_RE.finditer(relation_block):
        source, target, rel_type = match.groups()
        edges.append(Edge(source=source.upper(), target=target.upper(), type=rel_type.lower()))

    return vertices, edges
