"""Rapid model build and train pipeline.

Produces a deployable specialist adapter from a spec.
Works offline; training is simulated or lightweight when no GPU is present.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ModelSpec:
    name: str
    domain: str
    system_prompt: str
    examples: list[dict[str, str]] = field(default_factory=list)
    base: str = "phi4-mini"
    max_tokens: int = 512


class ModelBuilder:
    def __init__(self, out_dir: Path | None = None):
        self.out_dir = out_dir or Path("/tmp/openpalm-models")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.history: list[dict] = []

    def build(self, spec: ModelSpec) -> dict[str, Any]:
        """Create a specialist adapter file from the spec."""
        path = self.out_dir / f"{spec.name}.json"
        data = {
            "name": spec.name,
            "domain": spec.domain,
            "system_prompt": spec.system_prompt,
            "base": spec.base,
            "max_tokens": spec.max_tokens,
            "examples": spec.examples,
            "created": time.time(),
        }
        path.write_text(json.dumps(data, indent=2))
        self.history.append({"action": "build", "name": spec.name, "path": str(path)})
        return {"ok": True, "path": str(path), "name": spec.name}

    def train(self, name: str, epochs: int = 1) -> dict[str, Any]:
        """Lightweight training step. Logs progress; no heavy compute."""
        path = self.out_dir / f"{name}.json"
        if not path.exists():
            return {"ok": False, "error": "model not found"}
        data = json.loads(path.read_text())
        data["trained_epochs"] = data.get("trained_epochs", 0) + epochs
        data["last_train"] = time.time()
        path.write_text(json.dumps(data, indent=2))
        self.history.append({"action": "train", "name": name, "epochs": epochs})
        return {"ok": True, "name": name, "epochs": data["trained_epochs"]}

    def list(self) -> list[str]:
        return [p.stem for p in self.out_dir.glob("*.json")]


    def delete(self, name: str) -> bool:
        path = self.out_dir / f"{name}.json"
        if path.exists():
            path.unlink()
            self.history.append({"action": "delete", "name": name})
            return True
        return False

    def info(self, name: str) -> dict | None:
        data = self.load(name)
        if not data:
            return None
        path = self.out_dir / f"{name}.json"
        data["size_bytes"] = path.stat().st_size if path.exists() else 0
        return data

    def load(self, name: str) -> dict[str, Any] | None:
        path = self.out_dir / f"{name}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())
