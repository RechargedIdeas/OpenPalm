"""Train a RAMA state from collected records.

Supports manual (one pair) and automated (batch from collector) modes.
"""

from __future__ import annotations

from typing import Any

from .collector import TrainingCollector


class RAMATrainer:
    def __init__(self, states, collector: TrainingCollector):
        self.states = states
        self.collector = collector

    def train_manual(self, prompt: str, specialist: str) -> dict:
        """Teach the training state one route."""
        self.states.training.train_route(prompt, specialist)
        self.states.training._save_version(f"manual-{specialist}")
        return {"ok": True, "mode": "manual", "specialist": specialist}

    def train_auto(self, limit: int = 20) -> dict:
        """Replay recent collector records into the training state."""
        recs = self.collector.list(limit)
        taught = 0
        for r in recs:
            spec = r.get("specialist") or r.get("tags", ["general"])[0]
            self.states.training.train_route(r["prompt"], spec)
            taught += 1
        if taught:
            self.states.training._save_version(f"auto-{taught}")
        return {"ok": True, "mode": "auto", "taught": taught}

    def from_local(self, specialist: str, prompt: str, generate) -> dict:
        rec = self.collector.from_local(specialist, prompt, generate)
        self.train_manual(prompt, specialist)
        return {"ok": True, "record": rec}

    def from_api(self, name: str, prompt: str, response: str) -> dict:
        rec = self.collector.from_api(name, prompt, response)
        # Infer specialist from tags or default
        self.train_manual(prompt, name)
        return {"ok": True, "record": rec}
