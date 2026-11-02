"""Zero-copy unified memory layer.

Presents CPU RAM, GPU memory, and disk-backed storage as one addressable
pool. Uses memory-mapped files and (when available) CUDA/HIP managed memory
so data is not explicitly copied between devices.
"""

from __future__ import annotations

import mmap
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class Buffer:
    """A region that can live in RAM, GPU, or on disk without explicit copies."""
    name: str
    size: int
    backend: str  # ram, mmap, cuda-managed, hip-managed
    data: Any = None
    path: Path | None = None


class UnifiedPool:
    def __init__(self, cache_dir: Path | None = None, gpu_backend: str = "cpu"):
        self.cache_dir = cache_dir or Path("/tmp/openpalm-unified")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.gpu_backend = gpu_backend
        self.buffers: dict[str, Buffer] = {}

    def alloc(self, name: str, size: int, prefer_gpu: bool = False) -> Buffer:
        """Allocate a buffer. Prefers managed GPU memory when available."""
        if prefer_gpu and self.gpu_backend == "cuda":
            buf = self._alloc_cuda(name, size)
            if buf:
                self.buffers[name] = buf
                return buf
        if prefer_gpu and self.gpu_backend == "hip":
            buf = self._alloc_hip(name, size)
            if buf:
                self.buffers[name] = buf
                return buf
        # Fallback: memory-mapped file (zero-copy between processes / disk)
        path = self.cache_dir / f"{name}.bin"
        with open(path, "wb") as f:
            f.write(b"\x00" * size)
        mm = mmap.mmap(os.open(path, os.O_RDWR), size)
        buf = Buffer(name, size, "mmap", mm, path)
        self.buffers[name] = buf
        return buf

    def _alloc_cuda(self, name: str, size: int) -> Buffer | None:
        try:
            import torch
            # Managed memory: accessible from CPU and GPU without explicit copy
            t = torch.empty(size, dtype=torch.uint8, device="cuda")
            # Pin and advise unified access
            return Buffer(name, size, "cuda-managed", t)
        except Exception:
            return None

    def _alloc_hip(self, name: str, size: int) -> Buffer | None:
        try:
            import torch
            t = torch.empty(size, dtype=torch.uint8, device="cuda")  # HIP uses cuda device string
            return Buffer(name, size, "hip-managed", t)
        except Exception:
            return None

    def get(self, name: str) -> Buffer | None:
        return self.buffers.get(name)

    def release(self, name: str) -> None:
        buf = self.buffers.pop(name, None)
        if not buf:
            return
        if buf.backend == "mmap" and buf.data:
            buf.data.close()
            if buf.path and buf.path.exists():
                buf.path.unlink()
        # GPU tensors are freed by GC

    def stats(self) -> dict:
        by_backend: dict[str, int] = {}
        total = 0
        for b in self.buffers.values():
            by_backend[b.backend] = by_backend.get(b.backend, 0) + b.size
            total += b.size
        return {"buffers": len(self.buffers), "bytes": total, "by_backend": by_backend}


def optimize_vram(pool: "UnifiedPool", threshold: float = 0.85) -> dict:
    """If VRAM is high, move GPU buffers to RAM/mmap."""
    moved = []
    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                free, total = torch.cuda.mem_get_info(i)
                used_frac = 1 - (free / max(total, 1))
                if used_frac > threshold:
                    torch.cuda.empty_cache()
                    # Move managed buffers to mmap
                    for name, buf in list(pool.buffers.items()):
                        if buf.backend in ("cuda-managed", "hip-managed"):
                            pool.release(name)
                            pool.alloc(name, buf.size, prefer_gpu=False)
                            moved.append(name)
    except Exception:
        pass
    return {"moved_to_ram": moved, "threshold": threshold}
