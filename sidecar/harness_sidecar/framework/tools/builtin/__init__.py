"""Built-in tools for general agent use."""

from datetime import datetime
from typing import Any


def datetime_now(_: str = "") -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def list_ops(expr: str) -> str:
    """Simple list helpers: length, sort, unique. Input is comma-separated."""
    items = [x.strip() for x in expr.split(",") if x.strip()]
    if not items:
        return "empty"
    return f"count={len(items)} unique={len(set(items))} sorted={','.join(sorted(items))}"


def dict_lookup(spec: str) -> str:
    """Lookup key in key=value pairs. Format: key1=val1;key2=val2 | key"""
    if "|" not in spec:
        return "format: k=v;k2=v2 | key"
    data, key = spec.split("|", 1)
    pairs = {}
    for part in data.split(";"):
        if "=" in part:
            k, v = part.split("=", 1)
            pairs[k.strip()] = v.strip()
    return pairs.get(key.strip(), "not found")


def word_count(text: str) -> str:
    words = text.split()
    return f"words={len(words)} chars={len(text)}"


def extract_numbers(text: str) -> str:
    import re
    nums = re.findall(r"-?\d+(?:\.\d+)?", text)
    return ",".join(nums) if nums else "none"


BUILTIN = {
    "datetime": datetime_now,
    "list_ops": list_ops,
    "dict_lookup": dict_lookup,
    "word_count": word_count,
    "extract_numbers": extract_numbers,
}
