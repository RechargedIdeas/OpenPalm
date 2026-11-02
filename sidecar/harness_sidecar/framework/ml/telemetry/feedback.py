"""Feedback store for custom model improvement."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass
class Feedback:
    model: str
    prompt: str
    output: str
    rating: int  # 1-5
    note: str = ""
    ts: float = 0.0


class FeedbackStore:
    def __init__(self):
        self.items: list[Feedback] = []

    def add(self, model: str, prompt: str, output: str, rating: int, note: str = "") -> None:
        self.items.append(Feedback(model, prompt, output, rating, note, time.time()))

    def for_model(self, model: str) -> list[Feedback]:
        return [f for f in self.items if f.model == model]

    def avg_rating(self, model: str) -> float:
        items = self.for_model(model)
        if not items:
            return 0.0
        return sum(f.rating for f in items) / len(items)

    def export(self, model: str) -> list[dict]:
        return [
            {"prompt": f.prompt, "output": f.output, "rating": f.rating, "note": f.note}
            for f in self.for_model(model)
        ]
