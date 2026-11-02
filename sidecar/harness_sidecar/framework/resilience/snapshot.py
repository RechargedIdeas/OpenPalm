"""Atomic snapshots of agent state."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class SnapshotStore:
    def __init__(self, root: Path | None = None):
        self.root = root or Path("/tmp/openpalm-snapshots")
        self.root.mkdir(parents=True, exist_ok=True)
        self._current: dict[str, Any] = {}

    def take(self, state: dict[str, Any], label: str = "") -> str:
        """Atomic write via temp + rename."""
        sid = f"{int(time.time()*1000)}_{label or 'snap'}"
        path = self.root / f"{sid}.json"
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, default=str))
        tmp.rename(path)  # atomic on same filesystem
        self._current = state
        return sid

    def restore(self, sid: str) -> dict[str, Any] | None:
        path = self.root / f"{sid}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    def list(self) -> list[str]:
        return sorted(p.stem for p in self.root.glob("*.json"))

    def latest(self) -> dict[str, Any] | None:
        snaps = self.list()
        if not snaps:
            return None
        return self.restore(snaps[-1])
