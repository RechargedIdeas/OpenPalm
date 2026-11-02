"""Unified real-time monitor for all components.

Aggregates: activity logs, training jobs, RAMA versions, Watchdog alerts,
metrics, hardware, and sandbox status.
"""

from __future__ import annotations

import time
from typing import Any


class Monitor:
    def __init__(self):
        self.components = ["activity", "training", "rama", "watchdog", "metrics", "hardware", "sandbox"]

    def snapshot(self, app_state) -> dict:
        out: dict[str, Any] = {"ts": time.time()}
        # Activity logs
        if hasattr(app_state, "activity"):
            out["logs"] = app_state.activity.recent(20)
        else:
            out["logs"] = []
        # Training jobs
        if hasattr(app_state, "pipeline"):
            out["training"] = {
                "jobs": app_state.pipeline.list_jobs()[-10:],
                "active": app_state.pipeline.active(),
            }
        else:
            out["training"] = {"jobs": [], "active": []}
        # RAMA
        if hasattr(app_state, "rama"):
            out["rama"] = {"versions": len(app_state.rama.versions)}
        elif hasattr(app_state, "rama_states"):
            out["rama"] = app_state.rama_states.status()
        else:
            out["rama"] = {}
        # Watchdog
        if hasattr(app_state, "watchdog"):
            out["watchdog"] = app_state.watchdog.status()
        else:
            out["watchdog"] = {}
        if hasattr(app_state, "wd_trainer"):
            out["wd_train"] = app_state.wd_trainer.status()
        # Metrics
        try:
            from .metrics import collect
            out["metrics"] = collect()
        except Exception:
            out["metrics"] = {}
        # Hardware
        try:
            from .hardware import detect
            p = detect()
            out["hardware"] = {"backend": p.backend, "cores": p.cpu_cores, "gpus": len(p.gpus)}
        except Exception:
            out["hardware"] = {}
        # Sandbox
        if hasattr(app_state, "sandbox"):
            out["sandbox"] = app_state.sandbox.status()
        else:
            out["sandbox"] = {}
        return out
