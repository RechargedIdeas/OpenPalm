"""CUDA backend."""

from typing import Any
from .base import Backend


class CUDABackend(Backend):
    name = "cuda"

    def available(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
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
                "compute": f"{p.major}.{p.minor}",
            })
        return {"available": True, "devices": devs}

    def alloc(self, size: int) -> Any:
        import torch
        return torch.empty(size, dtype=torch.uint8, device="cuda")

    def empty_cache(self) -> None:
        if self.available():
            import torch
            torch.cuda.empty_cache()

    def set_memory_fraction(self, fraction: float) -> None:
        if self.available():
            import torch
            for i in range(self.device_count()):
                torch.cuda.set_per_process_memory_fraction(fraction, i)
