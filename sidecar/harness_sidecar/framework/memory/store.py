"""Hierarchical memory: working, episodic, semantic. Retrieval is selective."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryItem:
    content: str
    kind: str  # working, episodic, semantic
    score: float = 1.0
    ts: float = field(default_factory=time.time)
    meta: dict[str, Any] = field(default_factory=dict)


class MemoryStore:
    """In-process memory with relevance-ranked retrieval."""

    def __init__(self, max_working: int = 20, max_episodic: int = 200):
        self.working: list[MemoryItem] = []
        self.episodic: list[MemoryItem] = []
        self.semantic: list[MemoryItem] = []
        self.max_working = max_working
        self.max_episodic = max_episodic

    def add(self, content: str, kind: str = "working", meta: dict | None = None) -> None:
        item = MemoryItem(content=content, kind=kind, meta=meta or {})
        if kind == "working":
            self.working.append(item)
            if len(self.working) > self.max_working:
                # Promote oldest working to episodic
                old = self.working.pop(0)
                old.kind = "episodic"
                self.episodic.append(old)
        elif kind == "episodic":
            self.episodic.append(item)
            if len(self.episodic) > self.max_episodic:
                self.episodic.pop(0)
        else:
            self.semantic.append(item)

    def retrieve(self, query: str, limit: int = 5, kinds: list[str] | None = None) -> list[MemoryItem]:
        """Simple keyword overlap retrieval. Replace with embeddings in production."""
        pool: list[MemoryItem] = []
        kinds = kinds or ["working", "episodic", "semantic"]
        if "working" in kinds:
            pool.extend(self.working)
        if "episodic" in kinds:
            pool.extend(self.episodic)
        if "semantic" in kinds:
            pool.extend(self.semantic)

        q_tokens = set(query.lower().split())
        scored = []
        for item in pool:
            tokens = set(item.content.lower().split())
            overlap = len(q_tokens & tokens)
            if overlap > 0:
                scored.append((overlap / max(1, len(q_tokens)), item))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:limit]]

    def summary(self, max_items: int = 8) -> str:
        """Compact summary of recent working memory for context."""
        items = self.working[-max_items:]
        if not items:
            return ""
        return "\n".join(f"- {i.content[:120]}" for i in items)
