"""Model recommendation stub. Scores candidates against a hardware profile."""

from typing import Any


def recommend(profile: dict[str, Any]) -> list[dict[str, Any]]:
    """Return ranked model cards for the given hardware profile."""
    ram_gb = profile.get("ram_gb", 8)
    has_gpu = profile.get("has_gpu", False)

    candidates = [
        {
            "name": "phi4-mini",
            "params": "3.8B",
            "ram_gb": 2.5,
            "fits": ram_gb >= 6,
            "explanation": "This model runs on your computer. Writing an email takes about 10 seconds.",
        },
        {
            "name": "qwen3-1.7b",
            "params": "1.7B",
            "ram_gb": 1.2,
            "fits": ram_gb >= 4,
            "explanation": "Faster and smaller. Good if other apps are open.",
        },
        {
            "name": "llama3.1-8b",
            "params": "8B",
            "ram_gb": 5.0,
            "fits": ram_gb >= 10 or has_gpu,
            "explanation": "Higher quality writing. May be tight on 8 GB machines.",
        },
    ]
    return [c for c in candidates if c["fits"]]
