"""Efficient agent loop: retrieve → plan → act → verify → compress.

Designed so any model can run with minimal tokens and full tooling.
"""

from __future__ import annotations

from typing import Any, Callable

from ..memory.store import MemoryStore
from ..tools.registry import ToolRegistry
from ..skills.registry import SkillRegistry
from ..observability.tracker import Tracker
from .token_manager import TokenManager


class Agent:
    def __init__(
        self,
        generate: Callable[[str, str], str],
        model: str = "phi4-mini",
        memory: MemoryStore | None = None,
        tools: ToolRegistry | None = None,
        skills: SkillRegistry | None = None,
        active_skills: list[str] | None = None,
        max_steps: int = 4,
    ):
        self.generate = generate
        self.model = model
        self.memory = memory or MemoryStore()
        self.tools = tools or ToolRegistry()
        self.skills = skills or SkillRegistry()
        self.active_skills = active_skills or []
        self.tokens = TokenManager()
        self.tracker = Tracker()
        self.max_steps = max_steps

    def run(self, user_message: str, sources: list[str] | None = None) -> dict[str, Any]:
        """Full loop. Returns draft, claims, and token stats."""
        self.tracker.begin()
        sources = sources or []

        # 1. Store user message
        self.memory.add(user_message, kind="working")
        self.tracker.record("ingest", tokens_in=self.tokens.estimate(user_message))

        # 2. Selective retrieval
        retrieved = self.memory.retrieve(user_message, limit=4)
        context_bits = [m.content for m in retrieved]
        if sources:
            context_bits.extend(sources[:3])
        context = "\n".join(context_bits)
        context = self.tokens.compress(context, max_tokens=800)
        self.tracker.record("retrieve", tokens_in=self.tokens.estimate(context))

        # 3. Build minimal prompt
        tool_schema = self.tools.schema()
        skill_prompt = self.skills.system_prompt(self.active_skills)
        system = (
            "You are a careful agent. Use only the provided context. "
            "If you need a tool, reply with TOOL: name arg. "
            "Otherwise answer directly and cite sources."
        )
        if skill_prompt:
            system = system + "\n\n" + skill_prompt
        prompt = f"{system}\n\nContext:\n{context}\n\nTools:\n{tool_schema}\n\nUser: {user_message}\nAgent:"
        prompt = self.tokens.compress(prompt, self.tokens.budget.available)
        self.tracker.record("prompt", tokens_in=self.tokens.estimate(prompt))

        # 4. Generate (with optional tool loop)
        draft = ""
        for step in range(self.max_steps):
            out = self.generate(prompt, self.model)
            self.tracker.record("generate", tokens_out=self.tokens.estimate(out))
            if out.startswith("TOOL:"):
                parts = out[5:].strip().split(maxsplit=1)
                name = parts[0]
                arg = parts[1] if len(parts) > 1 else ""
                result = self.tools.call(name, arg)
                self.tracker.record("tool", tokens_in=result.tokens, note=name)
                prompt += f"\nTool result ({name}): {result.output}\nAgent:"
                continue
            draft = out
            break
        else:
            draft = draft or "I could not complete the request within the step limit."

        # 5. Store result
        self.memory.add(draft, kind="working")

        # 6. Lightweight claim check (reuse existing verify if available)
        claims = self._quick_claims(draft, sources + context_bits)

        return {
            "draft": draft,
            "claims": claims,
            "stats": self.tracker.summary(),
            "context_tokens": self.tokens.estimate(context),
        }

    def _quick_claims(self, draft: str, sources: list[str]) -> list[dict]:
        """Minimal claim grounding so the framework is self-contained."""
        import re
        sentences = re.split(r"(?<=[.!?])\s+", draft.strip())
        claims = []
        for s in sentences[:5]:
            s = s.strip()
            if len(s) < 12:
                continue
            supported = any(tok in " ".join(sources).lower() for tok in s.lower().split()[:4])
            claims.append({"text": s[:100], "status": "SUPPORTED" if supported else "UNSUPPORTED"})
        return claims
