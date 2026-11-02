"""Collect training data from local specialists and API models.

Produces reusable JSONL-style records that any model (RAMA or other) can train on.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable


class TrainingCollector:
    def __init__(self, store: Path | None = None):
        self.store = store or Path("/tmp/rama-train")
        self.store.mkdir(parents=True, exist_ok=True)
        self.records: list[dict] = []

    def from_local(self, specialist: str, prompt: str, generate: Callable[[str, str], str]) -> dict:
        """Run a local specialist and record the pair."""
        output = generate(prompt, specialist)
        rec = {
            "ts": time.time(),
            "source": "local",
            "specialist": specialist,
            "prompt": prompt,
            "output": output,
            "tags": ["local", specialist],
        }
        self._add(rec)
        return rec

    def from_api(self, name: str, prompt: str, response: str) -> dict:
        """Record a response obtained from an API model."""
        rec = {
            "ts": time.time(),
            "source": "api",
            "model": name,
            "prompt": prompt,
            "output": response,
            "tags": ["api", name],
        }
        self._add(rec)
        return rec

    def from_pair(self, prompt: str, output: str, tags: list[str] | None = None) -> dict:
        """Manual pair."""
        rec = {
            "ts": time.time(),
            "source": "manual",
            "prompt": prompt,
            "output": output,
            "tags": tags or ["manual"],
        }
        self._add(rec)
        return rec

    def _add(self, rec: dict) -> None:
        self.records.append(rec)
        path = self.store / "data.jsonl"
        with path.open("a") as f:
            f.write(json.dumps(rec) + "\n")

    def export(self, fmt: str = "jsonl") -> str:
        path = self.store / f"export.{fmt}"
        if fmt == "jsonl":
            path.write_text("\n".join(json.dumps(r) for r in self.records))
        else:
            path.write_text(json.dumps(self.records, indent=2))
        return str(path)

    def list(self, limit: int = 50) -> list[dict]:
        return self.records[-limit:]

    def clear(self) -> None:
        self.records.clear()
        p = self.store / "data.jsonl"
        if p.exists():
            p.unlink()
