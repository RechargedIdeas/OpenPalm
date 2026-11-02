"""Pre and post pipelines that keep context small and answers grounded."""

from typing import Any, Callable


def preprocess(message: str, memory_summary: str, sources: list[str], max_chars: int = 2000) -> str:
    """Build a tight context block."""
    parts = []
    if memory_summary:
        parts.append(f"Recent:\n{memory_summary}")
    if sources:
        joined = "\n---\n".join(sources)
        if len(joined) > max_chars:
            joined = joined[:max_chars] + "…"
        parts.append(f"Sources:\n{joined}")
    parts.append(f"Query: {message}")
    return "\n\n".join(parts)


def postprocess(draft: str, claims: list[dict], strict: bool = True) -> dict[str, Any]:
    """Flag unsupported claims and optionally block."""
    unsupported = [c for c in claims if c.get("status") == "UNSUPPORTED"]
    return {
        "draft": draft,
        "claims": claims,
        "can_copy": not (strict and unsupported),
        "unsupported_count": len(unsupported),
    }
