"""Simple telemetry visualization helpers (text + JSON for UI)."""

from .stream import ThoughtStream


def render_text(stream: ThoughtStream, n: int = 15) -> str:
    lines = []
    for t in stream.recent(n):
        lines.append(f"[{t['stage']:8}] {t['content']}")
    return "\n".join(lines)


def render_json(stream: ThoughtStream) -> dict:
    return {"summary": stream.summary(), "recent": stream.recent(20)}
