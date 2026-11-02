"""Compliance skill stub. Flags fair-housing risk vocabulary."""

RISK_PHRASES = ["must-see", "perfect for families", "ideal for", "perfect"]


def check(text: str) -> list[str]:
    """Return flagged phrases found in text."""
    lower = text.lower()
    return [p for p in RISK_PHRASES if p in lower]
