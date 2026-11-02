"""HIP/ROCm backend. Uses PyTorch HIP (device string 'cuda' under ROCm)."""

from typing import Any
from .base import Backend


class HIPBackend(Backend):
    name = "hip"

    def available(self) -> bool:
        try:
            import torch
            # ROCm builds report cuda available but hip version set
            return torch.cuda.is_available() and getattr(torch.version, "hip", None) is not None
        except Exception:
            return False

    def device_count(self) -> int:
        if not self.available():
            return 0
        import torch
        return torch.cuda.device_count()

    def info(self) -> dict:
        if not self.available():
            return {"available": False}
        import torch
        devs = []
        for i in range(self.device_count()):
            p = torch.cuda.get_device_properties(i)
            free, total = torch.cuda.mem_get_info(i)
            devs.append({
                "index": i,
                "name": p.name,
                "memory_mb": p.total_memory // (1024*1024),
                "free_mb": free // (1024*1024),
                "hip": getattr(torch.version, "hip", ""),
            })
        return {"available": True, "devices": devs}

    def alloc(self, size: int) -> Any:
        import torch
        return torch.empty(size, dtype=torch.uint8, device="cuda")

    def empty_cache(self) -> None:
        if self.available():
            import torch
            torch.cuda.empty_cache()
