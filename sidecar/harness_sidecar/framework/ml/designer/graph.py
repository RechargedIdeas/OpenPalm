"""Hybrid drag-and-drop + code model designer.

Graph is JSON: nodes (layers/ops) and edges. Editable in UI or as code.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Node:
    id: str
    kind: str  # input, embed, attention, ff, output, specialist, tool
    params: dict[str, Any] = field(default_factory=dict)
    x: float = 0.0
    y: float = 0.0


@dataclass
class Edge:
    src: str
    dst: str
    label: str = ""


class ModelGraph:
    def __init__(self, name: str = "untitled"):
        self.name = name
        self.nodes: dict[str, Node] = {}
        self.edges: list[Edge] = []

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, src: str, dst: str, label: str = "") -> None:
        if src in self.nodes and dst in self.nodes:
            self.edges.append(Edge(src, dst, label))

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "nodes": [
                {"id": n.id, "kind": n.kind, "params": n.params, "x": n.x, "y": n.y}
                for n in self.nodes.values()
            ],
            "edges": [{"src": e.src, "dst": e.dst, "label": e.label} for e in self.edges],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ModelGraph":
        g = cls(data.get("name", "untitled"))
        for n in data.get("nodes", []):
            g.add_node(Node(n["id"], n["kind"], n.get("params", {}), n.get("x", 0), n.get("y", 0)))
        for e in data.get("edges", []):
            g.add_edge(e["src"], e["dst"], e.get("label", ""))
        return g

    def to_code(self) -> str:
        """Emit a Python snippet that rebuilds the graph."""
        lines = [f'g = ModelGraph("{self.name}")']
        for n in self.nodes.values():
            lines.append(f'g.add_node(Node("{n.id}", "{n.kind}", {n.params!r}, {n.x}, {n.y}))')
        for e in self.edges:
            lines.append(f'g.add_edge("{e.src}", "{e.dst}", "{e.label}")')
        return "\n".join(lines)

    def validate(self) -> list[str]:
        """Return list of issues."""
        issues = []
        ids = set(self.nodes)
        for e in self.edges:
            if e.src not in ids:
                issues.append(f"edge src missing: {e.src}")
            if e.dst not in ids:
                issues.append(f"edge dst missing: {e.dst}")
        kinds = [n.kind for n in self.nodes.values()]
        if "input" not in kinds:
            issues.append("no input node")
        if "output" not in kinds:
            issues.append("no output node")
        return issues
