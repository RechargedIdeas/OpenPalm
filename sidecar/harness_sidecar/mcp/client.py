"""MCP client stub. Connects to external MCP servers and lists/calls tools."""

from typing import Any


class MCPClient:
    def __init__(self) -> None:
        self.connections: dict[str, bool] = {}

    def connect(self, name: str, config: dict[str, Any]) -> bool:
        """Stub: mark a connector as connected."""
        self.connections[name] = True
        return True

    def list_tools(self, name: str) -> list[dict[str, Any]]:
        """Stub: return empty tool list."""
        return []

    def call_tool(self, name: str, tool: str, args: dict[str, Any]) -> dict[str, Any]:
        """Stub: return a placeholder result."""
        return {"result": f"(stub) {tool} on {name}", "args": args}
