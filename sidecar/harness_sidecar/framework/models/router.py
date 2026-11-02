"""Route requests to the right specialist with fallback."""

from __future__ import annotations

from typing import Any, Callable

from .registry import ModelRegistry, Specialist
from .specialists import load_specialists


class ModelRouter:
    def __init__(self, generate: Callable[[str, str], str], model: str = "phi4-mini"):
        self.generate = generate
        self.model = model
        self.registry = ModelRegistry()
        load_specialists(self.registry)
        self._fallback_chain = ["phi4-mini", "qwen3-1.7b", "stub"]

    def run(self, specialist_name: str, prompt: str, model: str | None = None) -> dict[str, Any]:
        spec = self.registry.get(specialist_name)
        if not spec:
            return {"ok": False, "error": f"unknown specialist: {specialist_name}"}

        full = f"{spec.system_prompt}\n\nInput:\n{prompt}\n\nOutput:"
        used_model = model or self.model
        text = ""
        error = None

        # Try primary, then fallbacks
        for m in [used_model] + [x for x in self._fallback_chain if x != used_model]:
            try:
                text = self.generate(full, m)
                if spec.validate and not spec.validate(text):
                    continue
                used_model = m
                break
            except Exception as e:
                error = str(e)
                continue
        else:
            text = spec.fallback
            used_model = "fallback"

        return {
            "ok": True,
            "specialist": specialist_name,
            "domain": spec.domain,
            "model": used_model,
            "output": text.strip(),
            "error": error,
        }

    def list(self) -> list[dict]:
        return [
            {"name": n, "domain": self.registry.get(n).domain}
            for n in self.registry.list()
        ]
