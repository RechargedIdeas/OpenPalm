"""Registry of purpose-built specialist models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Specialist:
    name: str
    domain: str
    system_prompt: str
    validate: Callable[[str], bool] | None = None
    fallback: str = ""
    max_tokens: int = 512
    meta: dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    def __init__(self):
        self._models: dict[str, Specialist] = {}

    def register(self, spec: Specialist) -> None:
        self._models[spec.name] = spec

    def get(self, name: str) -> Specialist | None:
        return self._models.get(name)

    def list(self, domain: str | None = None) -> list[str]:
        if domain:
            return [n for n, s in self._models.items() if s.domain == domain]
        return list(self._models.keys())

    def domains(self) -> list[str]:
        return sorted({s.domain for s in self._models.values()})
