"""Default tools an agent can use. All return short strings."""

from .registry import ToolRegistry
from .builtin import BUILTIN


def make_default_registry() -> ToolRegistry:
    reg = ToolRegistry()

    def search_memory(query: str) -> str:
        return f"(memory search for '{query}' would return top matches)"

    def calculator(expr: str) -> str:
        try:
            # Safe eval for simple math
            allowed = set("0123456789+-*/(). ")
            if all(c in allowed for c in expr):
                return str(eval(expr))
            return "invalid expression"
        except Exception as e:
            return str(e)

    def summarize(text: str) -> str:
        words = text.split()
        if len(words) <= 40:
            return text
        return " ".join(words[:40]) + "…"

    reg.register("search_memory", search_memory)
    reg.register("calculator", calculator)
    reg.register("summarize", summarize)
    for name, fn in BUILTIN.items():
        reg.register(name, fn)
    return reg
