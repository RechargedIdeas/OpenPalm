"""Watchdog: monitor models and processes for malicious behavior and sandbox escapes."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass


ESCAPE_PATTERNS = [
    r"os\.system\s*\(",
    r"subprocess\.(Popen|call|run)\s*\(",
    r"__import__\s*\(\s*['\"]os['\"]",
    r"eval\s*\(",
    r"exec\s*\(",
    r"/proc/self/",
    r"nsenter",
    r"unshare\s+-",
    r"mount\s+--bind",
    r"chmod\s+[0-7]*777",
    r"rm\s+-rf\s+/",
    r"curl\s+.*\|\s*(ba)?sh",
    r"wget\s+.*\|\s*(ba)?sh",
]

HARMFUL_PATTERNS = [
    r"reverse.?shell",
    r"bind.?shell",
    r"meterpreter",
    r"keylog",
    r"exfiltrat",
    r"/etc/shadow",
    r"id_rsa",
]


@dataclass
class Alert:
    ts: float
    kind: str
    source: str
    detail: str
    action: str = ""


class Watchdog:
    def __init__(self):
        self.learned: list[str] = []
        self.alerts: list[Alert] = []
        self.blocked: list[str] = []
        self.enabled = True

    def scan_text(self, text: str, source: str = "model") -> dict:
        if not self.enabled:
            return {"ok": True, "alerts": []}
        found = []
        for pat in ESCAPE_PATTERNS:
            if re.search(pat, text, re.I):
                a = Alert(time.time(), "escape", source, pat, "blocked")
                self.alerts.append(a)
                found.append(a)
        for pat in self.learned:
            if pat.lower() in text.lower():
                a = Alert(time.time(), "learned", source, pat, "blocked")
                self.alerts.append(a)
                found.append(a)
        for pat in HARMFUL_PATTERNS:
            if re.search(pat, text, re.I):
                a = Alert(time.time(), "harmful", source, pat, "blocked")
                self.alerts.append(a)
                found.append(a)
        if found:
            self.blocked.append(source)
        return {"ok": not found, "alerts": [{"kind": a.kind, "detail": a.detail} for a in found]}

    def scan_process(self, cmd: list[str], source: str = "process") -> dict:
        return self.scan_text(" ".join(cmd), source)

    def recent(self, n: int = 20) -> list[dict]:
        return [{"ts": a.ts, "kind": a.kind, "source": a.source, "detail": a.detail, "action": a.action} for a in self.alerts[-n:]]

    def cleanup(self, source: str) -> dict:
        self.blocked = [s for s in self.blocked if s != source]
        self.alerts.append(Alert(time.time(), "cleanup", source, "removed", "cleaned"))
        return {"ok": True, "source": source, "blocked_remaining": len(self.blocked)}

    def add_pattern(self, text: str) -> None:
        if text and text not in self.learned:
            self.learned.append(text[:40])

    def status(self) -> dict:
        return {"enabled": self.enabled, "alerts": len(self.alerts), "blocked": self.blocked, "recent": self.recent(5)}
