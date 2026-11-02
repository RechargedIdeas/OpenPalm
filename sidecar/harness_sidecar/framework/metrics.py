"""Real-time performance metrics for CPU, RAM, and GPU backends."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field


@dataclass
class Metrics:
    ts: float
    cpu_percent: float
    ram_used_gb: float
    ram_total_gb: float
    ram_percent: float
    gpu_backend: str
    gpu_util: float
    vram_used_mb: int
    vram_total_mb: int
    vram_percent: float
    backend_stats: dict = field(default_factory=dict)


def _cpu_ram() -> tuple[float, float, float, float]:
    """Return cpu%, ram_used_gb, ram_total_gb, ram%."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.05)
        vm = psutil.virtual_memory()
        return cpu, vm.used / (1024**3), vm.total / (1024**3), vm.percent
    except Exception:
        pass
    # /proc fallback
    cpu = 0.0
    try:
        with open("/proc/stat") as f:
            line = f.readline()
        parts = [int(x) for x in line.split()[1:]]
        idle = parts[3]
        total = sum(parts)
        cpu = 100.0 * (1 - idle / max(total, 1))
    except Exception:
        pass
    ram_total = ram_used = 0.0
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                k, v = line.split(":")
                info[k.strip()] = int(v.split()[0])
        ram_total = info.get("MemTotal", 0) / (1024**2)
        ram_avail = info.get("MemAvailable", 0) / (1024**2)
        ram_used = ram_total - ram_avail
    except Exception:
        pass
    pct = (ram_used / ram_total * 100) if ram_total else 0
    return cpu, ram_used, ram_total, pct


def _cuda_stats() -> dict:
    try:
        import torch
        if not torch.cuda.is_available():
            return {}
        stats = []
        for i in range(torch.cuda.device_count()):
            free, total = torch.cuda.mem_get_info(i)
            used = total - free
            stats.append({
                "index": i,
                "name": torch.cuda.get_device_name(i),
                "vram_used_mb": used // (1024*1024),
                "vram_total_mb": total // (1024*1024),
                "util": torch.cuda.utilization(i) if hasattr(torch.cuda, "utilization") else 0,
            })
        return {"devices": stats}
    except Exception:
        return {}


def _hip_stats() -> dict:
    try:
        import subprocess
        r = subprocess.run(["rocm-smi", "--showuse", "--showmeminfo", "vram"], capture_output=True, text=True, timeout=2)
        if r.returncode == 0:
            return {"raw": r.stdout[:300]}
    except Exception:
        pass
    return {}


def _vulkan_stats() -> dict:
    # Vulkan has no standard runtime util query; report device presence
    return {"note": "Vulkan runtime stats require a loaded device"}


def collect(backend: str = "cpu") -> Metrics:
    cpu, ram_used, ram_total, ram_pct = _cpu_ram()
    gpu_util = 0.0
    vram_used = vram_total = 0
    bstats = {}

    if backend == "cuda":
        bstats = _cuda_stats()
        devs = bstats.get("devices", [])
        if devs:
            vram_used = sum(d["vram_used_mb"] for d in devs)
            vram_total = sum(d["vram_total_mb"] for d in devs)
            gpu_util = sum(d.get("util", 0) for d in devs) / len(devs)
    elif backend == "hip":
        bstats = _hip_stats()
    elif backend == "vulkan":
        bstats = _vulkan_stats()

    vram_pct = (vram_used / vram_total * 100) if vram_total else 0
    return Metrics(
        ts=time.time(),
        cpu_percent=round(cpu, 1),
        ram_used_gb=round(ram_used, 2),
        ram_total_gb=round(ram_total, 2),
        ram_percent=round(ram_pct, 1),
        gpu_backend=backend,
        gpu_util=round(gpu_util, 1),
        vram_used_mb=vram_used,
        vram_total_mb=vram_total,
        vram_percent=round(vram_pct, 1),
        backend_stats=bstats,
    )


def to_dict(m: Metrics) -> dict:
    return {
        "ts": m.ts,
        "cpu_percent": m.cpu_percent,
        "ram_used_gb": m.ram_used_gb,
        "ram_total_gb": m.ram_total_gb,
        "ram_percent": m.ram_percent,
        "gpu_backend": m.gpu_backend,
        "gpu_util": m.gpu_util,
        "vram_used_mb": m.vram_used_mb,
        "vram_total_mb": m.vram_total_mb,
        "vram_percent": m.vram_percent,
        "backend_stats": m.backend_stats,
    }
