"""Generate architecture diagrams from a ModelGraph.

Outputs Mermaid and a simple ASCII diagram.
"""

from __future__ import annotations

from .graph import ModelGraph


def to_mermaid(g: ModelGraph) -> str:
    lines = ["graph LR"]
    for n in g.nodes.values():
        label = f"{n.id}[{n.kind}]"
        lines.append(f"  {label}")
    for e in g.edges:
        lines.append(f"  {e.src} --> {e.dst}")
    return "\n".join(lines)


def to_ascii(g: ModelGraph) -> str:
    if not g.nodes:
        return "(empty)"
    # Simple left-to-right by x
    ordered = sorted(g.nodes.values(), key=lambda n: n.x)
    parts = []
    for n in ordered:
        parts.append(f"[{n.id}:{n.kind}]")
    return " → ".join(parts)


def to_svg_stub(g: ModelGraph) -> str:
    """Minimal SVG for embedding."""
    nodes = list(g.nodes.values())
    w = 120 * max(1, len(nodes)) + 40
    h = 80
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">']
    for i, n in enumerate(nodes):
        x = 20 + i * 120
        svg.append(f'<rect x="{x}" y="20" width="100" height="40" fill="#1e1e2e" stroke="#89b4fa"/>')
        svg.append(f'<text x="{x+50}" y="44" text-anchor="middle" fill="#cdd6f4" font-size="12">{n.id}</text>')
        if i > 0:
            svg.append(f'<line x1="{x-20}" y1="40" x2="{x}" y2="40" stroke="#89b4fa"/>')
    svg.append("</svg>")
    return "\n".join(svg)
