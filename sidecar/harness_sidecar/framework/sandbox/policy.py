"""Sandbox policy: what is allowed when isolation is on."""

from dataclasses import dataclass, field


@dataclass
class SandboxPolicy:
    isolate: bool = True
    network: bool = False          # no net by default
    filesystem: str = "ro"         # ro, rw, none
    allowed_paths: list[str] = field(default_factory=lambda: ["/tmp"])
    max_memory_mb: int = 512
    max_pids: int = 64
    allow_gpu: bool = False
    backend: str = "auto"          # auto, namespace, container, microvm

    def to_dict(self) -> dict:
        return {
            "isolate": self.isolate,
            "network": self.network,
            "filesystem": self.filesystem,
            "allowed_paths": self.allowed_paths,
            "max_memory_mb": self.max_memory_mb,
            "max_pids": self.max_pids,
            "allow_gpu": self.allow_gpu,
            "backend": self.backend,
        }
