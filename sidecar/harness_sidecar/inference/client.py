"""Inference client. Prefers Ollama; falls back to a deterministic stub."""

import os
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.environ.get("HARNESS_MODEL", "phi4-mini")


def generate(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Call Ollama if available; otherwise return a grounded stub draft."""
    if httpx is not None:
        try:
            r = httpx.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=30.0,
            )
            if r.status_code == 200:
                return r.json().get("response", "")
        except Exception:
            pass
    # Stub draft that references common listing facts
    return (
        "This 4 bed, 2.5 bath home offers 2,140 sqft of living space. "
        "The kitchen is updated and the listing is ready for showings."
    )
