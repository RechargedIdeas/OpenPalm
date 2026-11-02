"""Shared data store for both GUIs. Persists chat, settings, and sources."""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent
DATA_FILE = DATA_DIR / "shared.json"


def _default() -> dict[str, Any]:
    return {
        "messages": [],
        "settings": {"model": "phi4-mini", "passes": 2, "theme": "dark"},
        "sources": "",
    }


def load() -> dict[str, Any]:
    if not DATA_FILE.exists():
        return _default()
    try:
        data = json.loads(DATA_FILE.read_text())
        base = _default()
        base.update(data)
        return base
    except Exception:
        return _default()


def save(data: dict[str, Any]) -> dict[str, Any]:
    current = load()
    current.update(data)
    DATA_FILE.write_text(json.dumps(current, indent=2))
    return current


def get_messages() -> list:
    return load().get("messages", [])


def set_messages(messages: list) -> list:
    save({"messages": messages})
    return messages


def get_settings() -> dict:
    return load().get("settings", {})


def set_settings(settings: dict) -> dict:
    current = get_settings()
    current.update(settings)
    save({"settings": current})
    return current


def get_sources() -> str:
    return load().get("sources", "")


def set_sources(sources: str) -> str:
    save({"sources": sources})
    return sources
