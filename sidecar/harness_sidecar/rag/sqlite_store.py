"""SQLite vector store with brute-force cosine. Embeddings via Ollama when available."""

import json
import math
import sqlite3
from pathlib import Path
from typing import Any


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SQLiteStore:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, text TEXT, meta TEXT, emb TEXT)"
        )
        self.conn.commit()

    def add(self, text: str, embedding: list[float] | None = None, meta: dict | None = None) -> None:
        self.conn.execute(
            "INSERT INTO chunks (text, meta, emb) VALUES (?, ?, ?)",
            (text, json.dumps(meta or {}), json.dumps(embedding or [])),
        )
        self.conn.commit()

    def search(self, query_emb: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        rows = self.conn.execute("SELECT text, meta, emb FROM chunks").fetchall()
        scored = []
        for text, meta, emb in rows:
            e = json.loads(emb) if emb else []
            score = _cosine(query_emb, e) if e else 0.0
            scored.append({"text": text, "meta": json.loads(meta), "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored[:top_k]

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
