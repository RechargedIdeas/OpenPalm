"""Activity log: errors, debug, and command history."""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Entry:
    ts: float
    level: str  # info, debug, error, cmd
    message: str
    meta: dict = field(default_factory=dict)


class ActivityLog:
    def __init__(self, max_entries: int = 500):
        self.entries: list[Entry] = []
        self.max_entries = max_entries

    def add(self, level: str, message: str, meta: dict | None = None) -> None:
        self.entries.append(Entry(time.time(), level, message, meta or {}))
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def info(self, msg: str) -> None:
        self.add("info", msg)

    def debug(self, msg: str) -> None:
        self.add("debug", msg)

    def error(self, msg: str) -> None:
        self.add("error", msg)

    def cmd(self, msg: str) -> None:
        self.add("cmd", msg)

    def recent(self, n: int = 50, level: str | None = None) -> list[dict]:
        items = self.entries if not level else [e for e in self.entries if e.level == level]
        return [{"ts": e.ts, "level": e.level, "message": e.message} for e in items[-n:]]

    def export(self) -> str:
        lines = [f"[{e.level}] {e.message}" for e in self.entries]
        return "\n".join(lines)

    def clear(self) -> None:
        self.entries.clear()
