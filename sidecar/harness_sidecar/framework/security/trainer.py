"""Watchdog training: same shape as RAMA training.

Can learn from RAMA routes, feedback, and its own scan results.
"""

from __future__ import annotations

import time
from typing import Any


class WatchdogTrainer:
    def __init__(self, watchdog):
        self.wd = watchdog
        self.patterns_learned: list[dict] = []
        self.versions: list[dict] = []

    def train_from_alert(self, text: str, kind: str) -> dict:
        """Promote a confirmed alert into a learned pattern."""
        rec = {"ts": time.time(), "text": text[:80], "kind": kind, "source": "alert"}
        self.patterns_learned.append(rec)
        self.wd.add_pattern(text)
        self._save("alert")
        return {"ok": True, "learned": len(self.patterns_learned)}

    def train_from_rama(self, rama, limit: int = 10) -> dict:
        """Pull low-rated RAMA feedback and teach Watchdog those prompts are risky."""
        taught = 0
        for fb in getattr(rama, "feedback", [])[-limit:]:
            if fb.get("rating", 5) <= 2:
                self.train_from_alert(fb.get("prompt", ""), "rama-low")
                taught += 1
        return {"ok": True, "taught": taught}

    def train_manual(self, text: str, kind: str = "manual") -> dict:
        return self.train_from_alert(text, kind)

    def _save(self, label: str) -> str:
        vid = f"wd-{int(time.time()*1000)}"
        self.versions.append({"id": vid, "label": label, "ts": time.time(), "count": len(self.patterns_learned)})
        if len(self.versions) > 20:
            self.versions.pop(0)
        return vid

    def rollback(self) -> dict:
        if len(self.versions) < 2:
            return {"ok": False, "error": "no prior version"}
        prev = self.versions[-2]
        self.patterns_learned = self.patterns_learned[: prev["count"]]
        return {"ok": True, "restored": prev["id"]}

    def status(self) -> dict:
        return {
            "learned": len(self.patterns_learned),
            "versions": [{"id": v["id"], "label": v["label"]} for v in self.versions[-5:]],
        }
