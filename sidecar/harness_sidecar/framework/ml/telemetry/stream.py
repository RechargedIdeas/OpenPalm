"""Real-time thought stream and telemetry for model runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Thought:
    ts: float
    stage: str  # route, retrieve, generate, tool, verify, feedback
    content: str
    tokens: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


class ThoughtStream:
    def __init__(self, max_items: int = 200):
        self.items: list[Thought] = []
        self.max_items = max_items
        self.listeners: list = []

    def emit(self, stage: str, content: str, tokens: int = 0, meta: dict | None = None) -> None:
        t = Thought(time.time(), stage, content, tokens, meta or {})
        self.items.append(t)
        if len(self.items) > self.max_items:
            self.items.pop(0)
        for fn in self.listeners:
            try:
                fn(t)
            except Exception:
                pass

    def subscribe(self, fn) -> None:
        self.listeners.append(fn)

    def recent(self, n: int = 20) -> list[dict]:
        return [
            {"ts": t.ts, "stage": t.stage, "content": t.content[:200], "tokens": t.tokens}
            for t in self.items[-n:]
        ]

    def summary(self) -> dict:
        by_stage: dict[str, int] = {}
        tokens = 0
        for t in self.items:
            by_stage[t.stage] = by_stage.get(t.stage, 0) + 1
            tokens += t.tokens
        return {"events": len(self.items), "tokens": tokens, "by_stage": by_stage}
