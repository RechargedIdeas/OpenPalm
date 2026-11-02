"""Chunking strategies for email, PDF, and CSV."""

from typing import Any


def chunk_email(text: str) -> list[dict[str, Any]]:
    """Split an email into thread-aware chunks (stub)."""
    return [{"type": "email", "text": text[:2000]}]


def chunk_pdf(text: str) -> list[dict[str, Any]]:
    """Split a PDF by headings/paragraphs (stub)."""
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    return [{"type": "pdf", "text": p} for p in paras] or [{"type": "pdf", "text": text[:2000]}]


def chunk_csv(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One chunk per CSV row."""
    return [{"type": "csv", "text": str(row)} for row in rows]
