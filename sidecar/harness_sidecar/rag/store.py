"""SQLite cosine-similarity store stub."""

from typing import Any


class VectorStore:
    def __init__(self) -> None:
        self.chunks: list[dict[str, Any]] = []

    def add(self, chunk: dict[str, Any]) -> None:
        self.chunks.append(chunk)

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Stub: return first top_k chunks that contain a query token."""
        tokens = set(query.lower().split())
        scored = []
        for c in self.chunks:
            text = str(c.get("text", "")).lower()
            score = sum(1 for t in tokens if t in text)
            if score:
                scored.append((score, c))
        scored.sort(key=lambda x: -x[0])
        return [c for _, c in scored[:top_k]]
