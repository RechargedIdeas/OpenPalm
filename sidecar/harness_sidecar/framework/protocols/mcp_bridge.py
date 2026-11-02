"""MCP bridge: expose framework tools and specialists over MCP."""

from __future__ import annotations

from typing import Any

from ..tools.registry import ToolRegistry
from ..models.router import ModelRouter


class MCPBridge:
    def __init__(self, tools: ToolRegistry, router: ModelRouter):
        self.tools = tools
        self.router = router

    def list_tools(self) -> list[dict[str, Any]]:
        items = [{"name": n, "kind": "tool"} for n in self.tools.list()]
        items += [{"name": n, "kind": "specialist", "domain": self.router.registry.get(n).domain}
                  for n in self.router.registry.list()]
        return items

    def call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        if name in self.tools.list():
            arg = args.get("input", args.get("arg", ""))
            result = self.tools.call(name, str(arg))
            return {"ok": True, "output": result.output, "cached": result.cached}
        if self.router.registry.get(name):
            prompt = args.get("prompt", args.get("input", ""))
            return self.router.run(name, str(prompt))
        return {"ok": False, "error": f"unknown: {name}"}
