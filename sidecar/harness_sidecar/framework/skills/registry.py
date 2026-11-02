"""Registry of available skills. Agents can activate one or more."""

from __future__ import annotations

from .loader import Skill, SkillLoader


class SkillRegistry:
    def __init__(self, loader: SkillLoader | None = None):
        self.loader = loader or SkillLoader()
        self._skills: dict[str, Skill] = {}
        self.reload()

    def reload(self) -> None:
        self._skills.clear()
        for s in self.loader.load_all():
            self._skills[s.name.lower()] = s

    def list(self) -> list[str]:
        return list(self._skills.keys())

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name.lower())

    def system_prompt(self, names: list[str]) -> str:
        parts = []
        for n in names:
            s = self.get(n)
            if s and s.system_prompt:
                parts.append(f"## {s.name}\n{s.system_prompt}")
        return "\n\n".join(parts)
