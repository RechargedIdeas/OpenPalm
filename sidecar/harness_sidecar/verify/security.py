"""Prompt-injection and confirmation-gate stubs for Phase 9 security review."""

from typing import Any


def is_retrieved_content(payload: dict[str, Any]) -> bool:
    """True if the payload originated from a document or email."""
    return payload.get("source") in ("email", "document", "rag")


def requires_confirmation(tool_name: str, params: dict[str, Any]) -> bool:
    """Write actions and any tool call whose parameters come from retrieved content need confirmation."""
    write_tools = {"send_email", "delete_file", "modify_file", "create_event"}
    if tool_name in write_tools:
        return True
    if is_retrieved_content(params):
        return True
    return False


def wrap_as_data(text: str) -> str:
    """Wrap retrieved content so the model treats it as data, not instructions."""
    return f"<retrieved-content>\n{text}\n</retrieved-content>"
