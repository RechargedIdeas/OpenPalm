"""Self-healing: detect failure and recover from snapshot or fallback."""

from __future__ import annotations

from typing import Any, Callable

from .snapshot import SnapshotStore
from .state import StateManager


class SelfHealer:
    def __init__(self, snapshots: SnapshotStore, states: StateManager):
        self.snapshots = snapshots
        self.states = states
        self.failures = 0
        self.recoveries = 0

    def check(self, result: dict[str, Any]) -> bool:
        """Return True if result looks healthy."""
        if not result:
            return False
        if result.get("ok") is False:
            return False
        if "error" in result and result["error"] and not result.get("output"):
            return False
        return True

    def recover(self, generate: Callable, prompt: str) -> dict[str, Any]:
        """Try state failover, then snapshot restore, then deterministic stub."""
        self.failures += 1

        # 1. Failover to previous state
        if self.states.failover():
            self.recoveries += 1
            return {"ok": True, "recovered": "state", "output": "(recovered from parallel state)"}

        # 2. Restore latest snapshot
        snap = self.snapshots.latest()
        if snap:
            self.recoveries += 1
            return {"ok": True, "recovered": "snapshot", "output": str(snap)[:200]}

        # 3. Deterministic fallback
        self.recoveries += 1
        return {"ok": True, "recovered": "stub", "output": "Unable to complete. Please retry with simpler input."}

    def stats(self) -> dict:
        return {"failures": self.failures, "recoveries": self.recoveries}
