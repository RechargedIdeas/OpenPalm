"""Lightweight token and step tracking."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Step:
    kind: str
    tokens_in: int = 0
    tokens_out: int = 0
    duration_ms: float = 0.0
    note: str = ""


class Tracker:
    def __init__(self):
        self.steps: list[Step] = []
        self.total_in = 0
        self.total_out = 0
        self._start: float | None = None

    def begin(self) -> None:
        self._start = time.time()

    def record(self, kind: str, tokens_in: int = 0, tokens_out: int = 0, note: str = "") -> None:
        dur = 0.0
        if self._start:
            dur = (time.time() - self._start) * 1000
            self._start = time.time()
        self.steps.append(Step(kind, tokens_in, tokens_out, dur, note))
        self.total_in += tokens_in
        self.total_out += tokens_out

    def summary(self) -> dict:
        return {
            "steps": len(self.steps),
            "tokens_in": self.total_in,
            "tokens_out": self.total_out,
            "tokens_total": self.total_in + self.total_out,
            "last": self.steps[-1].kind if self.steps else None,
        }
