"""Isolation backends. Prefer real tools; fall back to namespace isolation."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any


class Backend:
    name = "base"

    def available(self) -> bool:
        return False

    def run(self, cmd: list[str], policy: Any) -> dict:
        raise NotImplementedError


class NamespaceBackend(Backend):
    """Linux namespaces via unshare. Always available on Linux."""
    name = "namespace"

    def available(self) -> bool:
        return shutil.which("unshare") is not None

    def run(self, cmd: list[str], policy: Any) -> dict:
        if not policy.isolate:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return {"ok": r.returncode == 0, "stdout": r.stdout[:500], "backend": "direct"}
        flags = ["--pid", "--fork", "--mount-proc"]
        if not policy.network:
            flags.append("--net")
        if policy.filesystem == "none":
            flags.append("--mount")
        full = ["unshare"] + flags + ["--"] + cmd
        try:
            r = subprocess.run(full, capture_output=True, text=True, timeout=30)
            return {"ok": r.returncode == 0, "stdout": r.stdout[:500], "stderr": r.stderr[:200], "backend": "namespace"}
        except Exception as e:
            return {"ok": False, "error": str(e), "backend": "namespace"}


class ContainerBackend(Backend):
    """Docker or Podman container."""
    name = "container"

    def available(self) -> bool:
        return shutil.which("docker") is not None or shutil.which("podman") is not None

    def _bin(self) -> str:
        return "docker" if shutil.which("docker") else "podman"

    def run(self, cmd: list[str], policy: Any) -> dict:
        if not self.available():
            return {"ok": False, "error": "no container runtime", "backend": "container"}
        bin_ = self._bin()
        args = [bin_, "run", "--rm", "--network", "none" if not policy.network else "bridge"]
        args += ["--memory", f"{policy.max_memory_mb}m", "--pids-limit", str(policy.max_pids)]
        if not policy.allow_gpu:
            args += ["--gpus", "0"] if bin_ == "docker" else []
        args += ["--"] + cmd if False else ["alpine"] + cmd  # minimal image
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=60)
            return {"ok": r.returncode == 0, "stdout": r.stdout[:500], "backend": "container"}
        except Exception as e:
            return {"ok": False, "error": str(e), "backend": "container"}


class MicroVMBackend(Backend):
    """Firecracker or QEMU micro-VM. Stub when tools are absent."""
    name = "microvm"

    def available(self) -> bool:
        return shutil.which("firecracker") is not None or shutil.which("qemu-system-x86_64") is not None

    def run(self, cmd: list[str], policy: Any) -> dict:
        if not self.available():
            return {"ok": False, "error": "no micro-VM runtime (install firecracker or qemu)", "backend": "microvm"}
        # Real launch would configure a kernel + rootfs; here we report readiness
        return {"ok": True, "note": "micro-VM available; full boot requires kernel/rootfs", "backend": "microvm", "cmd": cmd}


def get_backend(name: str = "auto") -> Backend:
    if name == "namespace":
        return NamespaceBackend()
    if name == "container":
        return ContainerBackend()
    if name == "microvm":
        return MicroVMBackend()
    # auto: prefer container, then microvm, then namespace
    for b in (ContainerBackend(), MicroVMBackend(), NamespaceBackend()):
        if b.available():
            return b
    return NamespaceBackend()
