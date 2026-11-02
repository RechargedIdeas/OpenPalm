"""Lightweight evaluation helpers for agent outputs."""

from typing import Any


def score_grounding(claims: list[dict]) -> float:
    """Fraction of claims that are SUPPORTED."""
    if not claims:
        return 1.0
    supported = sum(1 for c in claims if c.get("status") == "SUPPORTED")
    return supported / len(claims)


def score_brevity(draft: str, target_words: int = 80) -> float:
    """1.0 if under target, lower if longer."""
    words = len(draft.split())
    if words <= target_words:
        return 1.0
    return max(0.0, 1.0 - (words - target_words) / target_words)


def evaluate(result: dict[str, Any]) -> dict[str, Any]:
    """Return simple quality scores."""
    draft = result.get("draft", "")
    claims = result.get("claims", [])
    stats = result.get("stats", {})
    return {
        "grounding": round(score_grounding(claims), 2),
        "brevity": round(score_brevity(draft), 2),
        "tokens": stats.get("tokens_total", 0),
        "unsupported": sum(1 for c in claims if c.get("status") == "UNSUPPORTED"),
    }
