"""MCP server stub. Exposes harness tools over SSE."""

from typing import Any


HARNESS_TOOLS = [
    "search_files",
    "query_mls",
    "read_email",
    "draft_listing",
    "run_verification",
]


class MCPServer:
    def __init__(self) -> None:
        self.enabled = False
        self.sse_url = "http://127.0.0.1:0/sse"

    def list_tools(self) -> list[str]:
        return HARNESS_TOOLS

    def call_tool(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        return {"tool": name, "result": "(stub) not implemented", "args": args}
