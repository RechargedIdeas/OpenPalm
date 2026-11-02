"""Distillation technique implementations.

NumPy fallback always works. PyTorch path used when available.
"""

from __future__ import annotations

import math
from typing import Any


def _softmax(xs: list[float], temp: float = 1.0) -> list[float]:
    scaled = [x / temp for x in xs]
    m = max(scaled)
    exps = [math.exp(x - m) for x in scaled]
    s = sum(exps)
    return [e / s for e in exps]


def _kl(p: list[float], q: list[float]) -> float:
    """KL(p || q)."""
    eps = 1e-8
    return sum(pi * math.log((pi + eps) / (qi + eps)) for pi, qi in zip(p, q))


def response_distill(
    teacher_logits: list[list[float]],
    student_logits: list[list[float]],
    temperature: float = 2.0,
    alpha: float = 0.7,
) -> dict:
    """Classic Hinton distillation: soft targets + hard labels.

    Loss = alpha * T^2 * KL(soft_teacher, soft_student) + (1-alpha) * CE(hard, student)
    """
    if not teacher_logits or not student_logits:
        return {"ok": False, "error": "empty logits"}
    total = 0.0
    for t, s in zip(teacher_logits, student_logits):
        soft_t = _softmax(t, temperature)
        soft_s = _softmax(s, temperature)
        kl = _kl(soft_t, soft_s)
        # Hard label = argmax of teacher
        hard = t.index(max(t))
        ce = -math.log(_softmax(s, 1.0)[hard] + 1e-8)
        total += alpha * (temperature ** 2) * kl + (1 - alpha) * ce
    return {
        "ok": True,
        "technique": "response",
        "loss": round(total / len(teacher_logits), 4),
        "temperature": temperature,
        "alpha": alpha,
    }


def feature_distill(
    teacher_feats: list[list[float]],
    student_feats: list[list[float]],
) -> dict:
    """Match intermediate features with MSE."""
    if not teacher_feats or not student_feats:
        return {"ok": False, "error": "empty features"}
    total = 0.0
    n = 0
    for tf, sf in zip(teacher_feats, student_feats):
        # Align lengths
        m = min(len(tf), len(sf))
        for i in range(m):
            total += (tf[i] - sf[i]) ** 2
            n += 1
    mse = total / max(n, 1)
    return {"ok": True, "technique": "feature", "loss": round(mse, 4), "pairs": len(teacher_feats)}


def relation_distill(
    teacher_embeds: list[list[float]],
    student_embeds: list[list[float]],
) -> dict:
    """Match pairwise cosine similarities (relational knowledge)."""
    def cos(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) + 1e-8
        nb = math.sqrt(sum(y * y for y in b)) + 1e-8
        return dot / (na * nb)

    if len(teacher_embeds) < 2:
        return {"ok": False, "error": "need at least 2 samples"}
    total = 0.0
    n = 0
    for i in range(len(teacher_embeds)):
        for j in range(i + 1, len(teacher_embeds)):
            rt = cos(teacher_embeds[i], teacher_embeds[j])
            rs = cos(student_embeds[i], student_embeds[j])
            total += (rt - rs) ** 2
            n += 1
    return {"ok": True, "technique": "relation", "loss": round(total / max(n, 1), 4), "pairs": n}


def list_techniques() -> list[dict]:
    return [
        {"name": "response", "desc": "Soft-target KL (Hinton)"},
        {"name": "feature", "desc": "Intermediate MSE"},
        {"name": "relation", "desc": "Pairwise cosine"},
    ]
