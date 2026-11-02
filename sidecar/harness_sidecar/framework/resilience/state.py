"""Parallel state slots with failover."""

from __future__ import annotations

import copy
from typing import Any


class StateManager:
    def __init__(self, slots: int = 3):
        self.slots = slots
        self._states: list[dict[str, Any]] = [{} for _ in range(slots)]
        self.active = 0

    def get(self) -> dict[str, Any]:
        return self._states[self.active]

    def set(self, state: dict[str, Any]) -> None:
        self._states[self.active] = copy.deepcopy(state)

    def checkpoint(self) -> int:
        """Copy active state to next slot and switch."""
        nxt = (self.active + 1) % self.slots
        self._states[nxt] = copy.deepcopy(self._states[self.active])
        self.active = nxt
        return self.active

    def failover(self) -> bool:
        """Switch to previous slot if current is bad."""
        prev = (self.active - 1) % self.slots
        if self._states[prev]:
            self.active = prev
            return True
        return False

    def status(self) -> dict:
        return {"active": self.active, "slots": self.slots, "filled": sum(1 for s in self._states if s)}
