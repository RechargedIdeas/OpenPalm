"""Sandbox manager: default-on isolation with a toggle for direct hardware."""

from __future__ import annotations

import time
from typing import Any

from .policy import SandboxPolicy
from .backends import get_backend, NamespaceBackend


class SandboxManager:
    def __init__(self):
        self.policy = SandboxPolicy()  # isolate=True by default
        self.history: list[dict] = []

    def set_isolate(self, on: bool) -> None:
        self.policy.isolate = on

    def set_network(self, on: bool) -> None:
        self.policy.network = on

    def set_gpu(self, on: bool) -> None:
        self.policy.allow_gpu = on

    def status(self) -> dict:
        b = get_backend(self.policy.backend)
        return {
            "isolate": self.policy.isolate,
            "backend": b.name,
            "backend_available": b.available(),
            "policy": self.policy.to_dict(),
            "recent": self.history[-5:],
        }

    def run(self, cmd: list[str]) -> dict:
        """Run a command under the current policy."""
        backend = get_backend(self.policy.backend) if self.policy.isolate else NamespaceBackend()
        # If isolation is off, force direct
        if not self.policy.isolate:
            import subprocess
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            result = {"ok": r.returncode == 0, "stdout": r.stdout[:500], "backend": "direct"}
        else:
            result = backend.run(cmd, self.policy)
        result["ts"] = time.time()
        result["cmd"] = cmd
        self.history.append(result)
        if len(self.history) > 50:
            self.history.pop(0)
        return result

    def available_backends(self) -> dict:
        from .backends import NamespaceBackend, ContainerBackend, MicroVMBackend
        return {
            "namespace": NamespaceBackend().available(),
            "container": ContainerBackend().available(),
            "microvm": MicroVMBackend().available(),
        }
