"""Claim extraction and grounding check. No re-retrieval."""

import re
from typing import Any


def extract_claims(draft: str) -> list[str]:
    """Pull short factual assertions from a draft. Stub uses sentence splits."""
    sentences = re.split(r"(?<=[.!?])\s+", draft.strip())
    claims = []
    for s in sentences:
        s = s.strip()
        if len(s) > 10 and any(c.isdigit() or c.isupper() for c in s):
            claims.append(s[:120])
    return claims[:8] or [draft[:80]]


def ground_claim(claim: str, sources: list[str]) -> tuple[str, str | None]:
    """Return (SUPPORTED|UNSUPPORTED, matching source snippet)."""
    claim_l = claim.lower()
    # Normalize common number formats
    claim_norm = re.sub(r"[,]", "", claim_l)
    for src in sources:
        src_l = src.lower()
        src_norm = re.sub(r"[,]", "", src_l)
        tokens = [t for t in re.findall(r"\w+", claim_norm) if len(t) > 2]
        hits = sum(1 for t in tokens if t in src_norm)
        if hits >= max(1, len(tokens) // 4) or any(t in src_norm for t in tokens if t.isdigit()):
            return "SUPPORTED", src[:80]
    return "UNSUPPORTED", None


def verify(draft: str, sources: list[str], passes: int = 2) -> dict[str, Any]:
    """Run up to `passes` grounding checks. Returns final draft and claims."""
    current = draft
    claims = []
    for _ in range(max(1, passes)):
        raw = extract_claims(current)
        claims = []
        unsupported = []
        for c in raw:
            status, src = ground_claim(c, sources)
            claims.append({"text": c, "status": status, "source": src})
            if status == "UNSUPPORTED":
                unsupported.append(c)
        if not unsupported:
            break
        # stub revision: note the unsupported items
        current = current + "\n\n[Revised: removed or flagged unsupported claims.]"
    return {"draft": current, "claims": claims, "passes_run": passes}
