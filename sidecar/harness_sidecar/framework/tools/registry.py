"""Tool registry with result caching and compression."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolResult:
    name: str
    output: str
    cached: bool = False
    tokens: int = 0


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable[..., str]] = {}
        self._cache: dict[str, tuple[float, str]] = {}
        self.cache_ttl = 300  # seconds

    def register(self, name: str, fn: Callable[..., str]) -> None:
        self._tools[name] = fn

    def list(self) -> list[str]:
        return list(self._tools.keys())

    def call(self, name: str, *args: Any, use_cache: bool = True) -> ToolResult:
        if name not in self._tools:
            return ToolResult(name, f"Unknown tool: {name}")
        key = hashlib.md5(f"{name}:{args}".encode()).hexdigest()
        if use_cache and key in self._cache:
            ts, out = self._cache[key]
            if time.time() - ts < self.cache_ttl:
                return ToolResult(name, out, cached=True, tokens=len(out) // 4)
        out = self._tools[name](*args)
        # Compress long outputs
        if len(out) > 2000:
            out = out[:1000] + "\n…\n" + out[-500:]
        self._cache[key] = (time.time(), out)
        return ToolResult(name, out, tokens=len(out) // 4)

    def schema(self) -> str:
        """Compact tool descriptions for the model."""
        lines = []
        for name in self._tools:
            lines.append(f"- {name}")
        return "\n".join(lines) if lines else "(no tools)"
