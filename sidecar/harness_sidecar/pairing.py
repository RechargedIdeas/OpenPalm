"""Production-grade pairing: short codes, QR payloads, Tailscale-aware addresses."""

import secrets
import socket
import subprocess
import time
from typing import Any

# In-memory store; codes expire after 10 minutes
_codes: dict[str, dict[str, Any]] = {}
CODE_TTL = 600
PORT = 8765


def _lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def _tailscale_ip() -> str | None:
    try:
        r = subprocess.run(
            ["tailscale", "ip", "-4"],
            capture_output=True, text=True, timeout=3,
        )
        if r.returncode == 0:
            ip = r.stdout.strip().split("\n")[0].strip()
            if ip and not ip.startswith("error"):
                return ip
    except Exception:
        pass
    return None


def addresses() -> dict[str, Any]:
    lan = _lan_ip()
    ts = _tailscale_ip()
    return {
        "lan": f"http://{lan}:{PORT}",
        "tailscale": f"http://{ts}:{PORT}" if ts else None,
        "local": f"http://127.0.0.1:{PORT}",
        "preferred": f"http://{ts}:{PORT}" if ts else f"http://{lan}:{PORT}",
        "tailscale_active": ts is not None,
    }


def create_code() -> dict[str, Any]:
    code = secrets.token_hex(3).upper()  # 6 hex chars
    addrs = addresses()
    entry = {
        "code": code,
        "created": time.time(),
        "addresses": addrs,
        "redeemed": False,
    }
    _codes[code] = entry
    # prune old
    now = time.time()
    for k in list(_codes):
        if now - _codes[k]["created"] > CODE_TTL:
            del _codes[k]
    return {
        "code": code,
        "expires_in": CODE_TTL,
        "qr_payload": _qr_payload(code, addrs),
        "addresses": addrs,
    }


def _qr_payload(code: str, addrs: dict) -> str:
    url = addrs["preferred"]
    return f"openpalm://pair?code={code}&url={url}"


def redeem(code: str) -> dict[str, Any] | None:
    code = code.strip().upper()
    entry = _codes.get(code)
    if not entry:
        return None
    if time.time() - entry["created"] > CODE_TTL:
        del _codes[code]
        return None
    entry["redeemed"] = True
    return {
        "ok": True,
        "code": code,
        "url": entry["addresses"]["preferred"],
        "addresses": entry["addresses"],
    }


def status() -> dict[str, Any]:
    active = [c for c, e in _codes.items() if time.time() - e["created"] < CODE_TTL]
    return {
        "active_codes": len(active),
        "addresses": addresses(),
    }
