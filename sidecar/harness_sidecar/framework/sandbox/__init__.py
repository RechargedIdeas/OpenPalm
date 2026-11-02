"""Sandboxing nervous system.

Every process runs isolated by default. Users can toggle off for direct hardware.
Backends: namespaces (unshare), containers (docker/podman), micro-VM (firecracker/qemu).
"""

from .manager import SandboxManager, SandboxPolicy
from .backends import get_backend

__all__ = ["SandboxManager", "SandboxPolicy", "get_backend"]
