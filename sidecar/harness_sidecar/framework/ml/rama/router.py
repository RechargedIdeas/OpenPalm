"""RAMA: Router And Model Architecture.

A local micro-router that:
- Acts as a small language model for simple tasks
- Routes complex tasks to the best available specialist, local model, or API
- Supports MoE (mixture of experts) and MoA (mixture of agents) patterns
- Works offline; falls back to local specialists
"""

from __future__ import annotations

import re
from typing import Any, Callable

from ...models.router import ModelRouter
from ..telemetry.stream import ThoughtStream


# Keyword → specialist routing table (trainable in production)
DEFAULT_ROUTES = {
    r"\b(lint|syntax|style|unused)\b": "linter",
    r"\b(spell|typo|correct)\b": "spellcheck",
    r"\b(translate|translation)\b": "translate",
    r"\b(code|function|script|program)\b": "coder",
    r"\b(design|layout|ui|ux)\b": "designer",
    r"\b(math|calculate|equation|solve)\b": "math",
    r"\b(science|physics|chemistry|biology)\b": "science",
    r"\b(cad|3d|geometry|dimension)\b": "cad",
    r"\b(music|melody|tempo|key)\b": "music",
    r"\b(art|palette|composition)\b": "art",
    r"\b(tool|call|invoke)\b": "tooluse",
}


class RAMA:
    def __init__(
        self,
        generate: Callable[[str, str], str],
        model_router: ModelRouter | None = None,
        stream: ThoughtStream | None = None,
    ):
        self.generate = generate
        self.router = model_router or ModelRouter(generate)
        self.stream = stream or ThoughtStream()
        self.routes = dict(DEFAULT_ROUTES)
        self.local_models = ["phi4-mini", "qwen3-1.7b"]
        self.api_models: dict[str, str] = {}  # name → endpoint
        self.agents: dict[str, Callable] = {}  # MoA: name → callable
        self.versions: list[dict] = []  # backup states
        self.feedback: list[dict] = []
        self._save_version("init")

    def register_agent(self, name: str, fn: Callable[[str], str]) -> None:
        self.agents[name] = fn

    def register_api(self, name: str, endpoint: str) -> None:
        self.api_models[name] = endpoint

    def route(self, prompt: str) -> str:
        """Pick the best specialist or agent for the prompt."""
        self.stream.emit("route", f"routing: {prompt[:80]}")
        pl = prompt.lower()
        for pattern, specialist in self.routes.items():
            if re.search(pattern, pl):
                self.stream.emit("route", f"matched {specialist}")
                return specialist
        # Default: try local micro response
        return "local"

    def run(self, prompt: str, mode: str = "auto") -> dict[str, Any]:
        """
        mode:
          auto  — route then execute
          moe   — mixture of experts (run top specialists, pick best)
          moa   — mixture of agents (fan out to registered agents)
          local — force local micro model
        """
        self.stream.emit("start", prompt[:100])

        if mode == "local" or self.route(prompt) == "local":
            out = self._local(prompt)
            self.stream.emit("generate", out[:100], tokens=len(out) // 4)
            return {"ok": True, "mode": "local", "output": out, "stream": self.stream.recent(5)}

        target = self.route(prompt)

        if mode == "moe":
            return self._moe(prompt, target)

        if mode == "moa":
            return self._moa(prompt)

        # Single specialist
        result = self.router.run(target, prompt)
        self.stream.emit("generate", result.get("output", "")[:100])
        return {**result, "mode": "specialist", "stream": self.stream.recent(5)}

    def _local(self, prompt: str) -> str:
        """Micro LM path: short, local, offline."""
        sys = "You are RAMA, a small local router. Answer briefly and accurately."
        return self.generate(f"{sys}\n\n{prompt}", self.local_models[0])

    def _moe(self, prompt: str, primary: str) -> dict[str, Any]:
        """Run primary + one fallback specialist, return the longer/better output."""
        self.stream.emit("moe", f"experts: {primary}")
        results = []
        for name in [primary, "tooluse"]:
            r = self.router.run(name, prompt)
            results.append(r)
            self.stream.emit("moe", f"{name}: {r.get('output','')[:40]}")
        best = max(results, key=lambda x: len(x.get("output", "")))
        return {**best, "mode": "moe", "candidates": len(results), "stream": self.stream.recent(8)}

    def _moa(self, prompt: str) -> dict[str, Any]:
        """Fan out to registered agents and aggregate."""
        if not self.agents:
            return self.run(prompt, mode="moe")
        self.stream.emit("moa", f"agents: {list(self.agents)}")
        outs = []
        for name, fn in self.agents.items():
            try:
                o = fn(prompt)
                outs.append({"agent": name, "output": o})
                self.stream.emit("moa", f"{name}: {o[:40]}")
            except Exception as e:
                self.stream.emit("moa", f"{name} error: {e}")
        combined = "\n".join(f"[{o['agent']}] {o['output']}" for o in outs)
        return {"ok": True, "mode": "moa", "output": combined, "agents": len(outs), "stream": self.stream.recent(8)}


    def _save_version(self, label: str = "") -> str:
        """Snapshot current routes and config."""
        import time
        vid = f"v{int(time.time()*1000)}"
        self.versions.append({
            "id": vid,
            "label": label,
            "routes": dict(self.routes),
            "ts": time.time(),
        })
        # Keep last 20
        if len(self.versions) > 20:
            self.versions.pop(0)
        return vid

    def rollback(self, vid: str | None = None) -> bool:
        """Restore a previous version. Latest if vid is None."""
        if not self.versions:
            return False
        target = None
        if vid:
            for v in self.versions:
                if v["id"] == vid:
                    target = v
                    break
        else:
            target = self.versions[-2] if len(self.versions) > 1 else self.versions[-1]
        if not target:
            return False
        self.routes = dict(target["routes"])
        self.stream.emit("rollback", f"restored {target['id']}")
        return True

    def list_versions(self) -> list[dict]:
        return [{"id": v["id"], "label": v["label"], "ts": v["ts"]} for v in self.versions]

    def add_feedback(self, prompt: str, output: str, rating: int, note: str = "") -> dict:
        """Record feedback and auto-train if rating is low."""
        import time
        entry = {"prompt": prompt, "output": output, "rating": rating, "note": note, "ts": time.time()}
        self.feedback.append(entry)
        trained = False
        if rating <= 2 and note:
            # Low rating: try to learn a better route from the note
            self.train_route(prompt, note.strip().lower())
            self._save_version(f"feedback-{rating}")
            trained = True
        elif rating >= 4:
            # High rating: reinforce current route
            target = self.route(prompt)
            if target != "local":
                self.train_route(prompt, target)
                self._save_version(f"reinforce-{rating}")
                trained = True
        return {"ok": True, "trained": trained, "versions": len(self.versions)}

    def train_route(self, prompt: str, specialist: str) -> None:
        """Add a routing example (simple keyword learn)."""
        words = [w for w in re.findall(r"\w+", prompt.lower()) if len(w) > 3]
        if words:
            pattern = r"\b(" + "|".join(words[:3]) + r")\b"
            self.routes[pattern] = specialist
            self.stream.emit("train", f"learned {specialist} from '{prompt[:40]}'")
