"""Load skills from markdown files or Python modules."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Skill:
    name: str
    description: str
    system_prompt: str = ""
    tools: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


class SkillLoader:
    def __init__(self, root: Path | None = None):
        self.root = root or Path(__file__).parent / "packs"

    def load_md(self, path: Path) -> Skill:
        text = path.read_text()
        lines = text.strip().splitlines()
        name = path.stem
        description = ""
        body_start = 0
        if lines and lines[0].startswith("# "):
            name = lines[0][2:].strip()
            body_start = 1
        if body_start < len(lines) and lines[body_start].strip():
            description = lines[body_start].strip()
            body_start += 1
        system = "\n".join(lines[body_start:]).strip()
        return Skill(name=name, description=description, system_prompt=system)

    def load_py(self, path: Path) -> Skill | None:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "SKILL"):
            s = mod.SKILL
            return Skill(
                name=s.get("name", path.stem),
                description=s.get("description", ""),
                system_prompt=s.get("system_prompt", ""),
                tools=s.get("tools", []),
                meta=s.get("meta", {}),
            )
        return None

    def load_all(self) -> list[Skill]:
        skills = []
        if not self.root.exists():
            return skills
        for p in sorted(self.root.glob("*.md")):
            skills.append(self.load_md(p))
        for p in sorted(self.root.glob("*.py")):
            if p.name.startswith("_"):
                continue
            s = self.load_py(p)
            if s:
                skills.append(s)
        return skills
