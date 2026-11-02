"""Model download and self-test helper. Calls Ollama when available."""

import os
from typing import Any

try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")


def download_model(name: str) -> dict[str, Any]:
    """Pull a model via Ollama. Returns status."""
    if httpx is None:
        return {"ok": False, "reason": "httpx not installed"}
    try:
        r = httpx.post(f"{OLLAMA_URL}/api/pull", json={"name": name, "stream": False}, timeout=300.0)
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def self_test(model: str, prompt: str = "Hello") -> dict[str, Any]:
    """Generate a short reply to confirm the model works."""
    if httpx is None:
        return {"ok": False, "reason": "httpx not installed"}
    try:
        r = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": 20}},
            timeout=60.0,
        )
        if r.status_code == 200:
            text = r.json().get("response", "")
            return {"ok": True, "sample": text[:80]}
        return {"ok": False, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


def force_cpu() -> None:
    """Set environment so Ollama skips fragile iGPU acceleration."""
    os.environ["OLLAMA_VULKAN"] = "0"
