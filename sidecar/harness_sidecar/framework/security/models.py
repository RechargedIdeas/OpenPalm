"""Security specialist models that work with the Watchdog."""

from .watchdog import Watchdog

SECURITY_MODELS = [
    ("guard", "Scan outputs for escape and harmful patterns"),
    ("policy", "Enforce allow/deny rules before execution"),
    ("auditor", "Review recent alerts and recommend action"),
    ("isolator", "Recommend sandbox tightening after an alert"),
    ("cleaner", "Plan cleanup of an escaped process"),
]


class SecurityModel:
    def __init__(self, name: str, desc: str, watchdog: Watchdog):
        self.name = name
        self.desc = desc
        self.wd = watchdog

    def run(self, text: str) -> dict:
        if self.name == "guard":
            return {"model": "guard", **self.wd.scan_text(text, "guard")}
        if self.name == "policy":
            r = self.wd.scan_process(text.split(), "policy")
            return {"model": "policy", "allow": r["ok"], **r}
        if self.name == "auditor":
            return {"model": "auditor", "alerts": self.wd.recent(10)}
        if self.name == "isolator":
            return {"model": "isolator", "advice": "Tighten: disable network, drop GPU, lower PIDs"}
        if self.name == "cleaner":
            return {"model": "cleaner", "plan": ["stop process", "revoke tokens", "wipe temp", "alert user"]}
        return {"model": self.name, "desc": self.desc}


def list_security() -> list[dict]:
    return [{"name": n, "desc": d} for n, d in SECURITY_MODELS]
