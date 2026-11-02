"""Agent Client Protocol (ACP) handler.

Minimal ACP-style request/response for agent sessions.
"""

from __future__ import annotations

import time
from typing import Any


class ACPHandler:
    """Handles ACP-style messages: session/prompt, session/cancel, etc."""

    def __init__(self):
        self.sessions: dict[str, dict[str, Any]] = {}

    def handle(self, msg: dict[str, Any]) -> dict[str, Any]:
        method = msg.get("method", "")
        params = msg.get("params", {})
        mid = msg.get("id")

        if method == "session/new":
            sid = f"s{int(time.time()*1000)}"
            self.sessions[sid] = {"created": time.time(), "history": []}
            return {"id": mid, "result": {"sessionId": sid}}

        if method == "session/prompt":
            sid = params.get("sessionId")
            if sid not in self.sessions:
                return {"id": mid, "error": {"code": -32602, "message": "unknown session"}}
            prompt = params.get("prompt", "")
            self.sessions[sid]["history"].append({"role": "user", "content": prompt})
            # Caller wires the actual agent run
            return {"id": mid, "result": {"sessionId": sid, "prompt": prompt, "status": "accepted"}}

        if method == "session/cancel":
            sid = params.get("sessionId")
            if sid in self.sessions:
                self.sessions[sid]["cancelled"] = True
            return {"id": mid, "result": {"ok": True}}

        if method == "session/list":
            return {"id": mid, "result": {"sessions": list(self.sessions.keys())}}

        return {"id": mid, "error": {"code": -32601, "message": f"unknown method: {method}"}}
