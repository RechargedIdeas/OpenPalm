"""Parallel RAMA states: backup, working, and training.

- backup: last known good snapshot; used for failover
- working: the live router users talk to
- training: isolated state that learns without affecting working
"""

from __future__ import annotations

import copy
import time
from typing import Any


class RAMAStates:
    def __init__(self, rama_factory):
        """rama_factory() returns a fresh RAMA instance."""
        self.factory = rama_factory
        self.working = rama_factory()
        self.backup = copy.deepcopy(self.working)
        self.training = rama_factory()
        self._history: list[dict] = []

    def snapshot_backup(self, label: str = "auto") -> str:
        """Copy working → backup."""
        self.backup = copy.deepcopy(self.working)
        vid = f"bak-{int(time.time()*1000)}"
        self._history.append({"id": vid, "label": label, "ts": time.time()})
        return vid

    def failover(self) -> dict:
        """Promote backup → working."""
        self.working = copy.deepcopy(self.backup)
        return {"ok": True, "note": "working restored from backup"}

    def promote_training(self) -> dict:
        """Promote training → working, then snapshot backup."""
        self.snapshot_backup("pre-promote")
        self.working = copy.deepcopy(self.training)
        return {"ok": True, "note": "training promoted to working"}

    def reset_training(self) -> None:
        self.training = self.factory()

    def status(self) -> dict:
        return {
            "working_versions": len(self.working.versions),
            "backup_versions": len(self.backup.versions),
            "training_versions": len(self.training.versions),
            "history": self._history[-5:],
        }
