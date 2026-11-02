"""Token accounting and context compression to minimize usage."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenBudget:
    max_context: int = 4096
    reserved_response: int = 512
    reserved_system: int = 256

    @property
    def available(self) -> int:
        return max(0, self.max_context - self.reserved_response - self.reserved_system)


class TokenManager:
    """Estimates tokens and compresses context to stay within budget."""

    def __init__(self, budget: TokenBudget | None = None):
        self.budget = budget or TokenBudget()
        self.used = 0

    def estimate(self, text: str) -> int:
        """Rough token estimate: ~4 chars per token, with punctuation adjustment."""
        if not text:
            return 0
        words = len(text.split())
        chars = len(text)
        return max(words, chars // 4)

    def compress(self, text: str, max_tokens: int) -> str:
        """Truncate or summarize to fit max_tokens."""
        if self.estimate(text) <= max_tokens:
            return text
        # Prefer keeping the start and end
        target_chars = max_tokens * 4
        if len(text) <= target_chars:
            return text
        half = target_chars // 2
        return text[:half].rstrip() + "\n…\n" + text[-half:].lstrip()

    def pack_messages(self, messages: list[dict[str, Any]], system: str = "") -> tuple[list[dict], int]:
        """Pack messages within available budget, dropping oldest first."""
        avail = self.budget.available - self.estimate(system)
        packed: list[dict] = []
        used = 0
        for msg in reversed(messages):
            cost = self.estimate(msg.get("content", ""))
            if used + cost > avail:
                break
            packed.append(msg)
            used += cost
        packed.reverse()
        self.used = used + self.estimate(system)
        return packed, self.used

    def reset(self) -> None:
        self.used = 0
