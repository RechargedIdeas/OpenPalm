"""Adaptive hardware detection and resource allocation.

Detects CUDA, HIP/ROCm, Vulkan, and AMD. Scales from 1 core to multi-GPU.
Provides optimization hints and a unified-memory friendly profile.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field


@dataclass
class GPUInfo:
    index: int
    name: str
    backend: str  # cuda, hip, vulkan
    memory_mb: int = 0
    vendor: str = ""  # nvidia, amd, intel, other


@dataclass
class HardwareProfile:
    cpu_count: int
    gpu_count: int
    gpus: list[GPUInfo] = field(default_factory=list)
    gpu_names: list[str] = field(default_factory=list)
    memory_gb: float = 4.0
    mode: str = "cpu"  # cpu, single-gpu, multi-gpu
    backend: str = "cpu"  # cpu, cuda, hip, vulkan
    workers: int = 1
    batch_size: int = 1
    unified_memory: bool = False
    gpu_memory_fraction: float = 0.8


def _run(cmd: list[str]) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def _detect_cuda() -> list[GPUInfo]:
    gpus = []
    try:
        import torch
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                gpus.append(GPUInfo(
                    index=i,
                    name=props.name,
                    backend="cuda",
                    memory_mb=props.total_memory // (1024 * 1024),
                    vendor="nvidia",
                ))
            return gpus
    except Exception:
        pass
    # nvidia-smi fallback
    out = _run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
    if out:
        for i, line in enumerate(out.splitlines()):
            parts = [p.strip() for p in line.split(",")]
            name = parts[0] if parts else "NVIDIA GPU"
            mem = 0
            if len(parts) > 1:
                try:
                    mem = int(parts[1].split()[0])
                except Exception:
                    pass
            gpus.append(GPUInfo(i, name, "cuda", mem, "nvidia"))
    return gpus


def _detect_hip() -> list[GPUInfo]:
    gpus = []
    # rocm-smi
    out = _run(["rocm-smi", "--showproductname", "--showmeminfo", "vram"])
    if out and "GPU" in out:
        # Minimal parse: count devices
        lines = [l for l in out.splitlines() if "GPU" in l or "Card" in l]
        for i, line in enumerate(lines[:8]):
            gpus.append(GPUInfo(i, line.strip()[:40], "hip", 0, "amd"))
    # hipconfig
    if not gpus and shutil.which("hipconfig"):
        gpus.append(GPUInfo(0, "AMD GPU (HIP)", "hip", 0, "amd"))
    return gpus


def _detect_vulkan() -> list[GPUInfo]:
    gpus = []
    out = _run(["vulkaninfo", "--summary"])
    if not out:
        return gpus
    for i, line in enumerate(out.splitlines()):
        if "deviceName" in line or "GPU" in line:
            name = line.split("=")[-1].strip() if "=" in line else line.strip()
            if name and len(gpus) < 4:
                vendor = "amd" if "AMD" in name or "Radeon" in name else "other"
                gpus.append(GPUInfo(len(gpus), name[:40], "vulkan", 0, vendor))
    return gpus


def detect() -> HardwareProfile:
    cpu = os.cpu_count() or 1

    # Memory
    mem_gb = 4.0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    mem_gb = int(line.split()[1]) / (1024 ** 2)
                    break
    except Exception:
        pass

    # GPU backends in priority order
    gpus = _detect_cuda()
    backend = "cuda" if gpus else ""
    if not gpus:
        gpus = _detect_hip()
        backend = "hip" if gpus else ""
    if not gpus:
        gpus = _detect_vulkan()
        backend = "vulkan" if gpus else ""

    gpu_count = len(gpus)
    gpu_names = [g.name for g in gpus]

    if gpu_count >= 2:
        mode = "multi-gpu"
        workers = min(cpu, gpu_count * 4)
        batch = 8
    elif gpu_count == 1:
        mode = "single-gpu"
        workers = min(cpu, 8)
        batch = 4
    else:
        mode = "cpu"
        backend = "cpu"
        workers = max(1, min(cpu, 4))
        batch = 1

    workers = max(1, min(workers, 64))

    # Unified memory available on modern CUDA and some AMD
    unified = backend in ("cuda", "hip") and mem_gb >= 8

    return HardwareProfile(
        cpu_count=cpu,
        gpu_count=gpu_count,
        gpus=gpus,
        gpu_names=gpu_names,
        memory_gb=round(mem_gb, 1),
        mode=mode,
        backend=backend,
        workers=workers,
        batch_size=batch,
        unified_memory=unified,
        gpu_memory_fraction=0.85 if mem_gb > 16 else 0.7,
    )


def apply(profile: HardwareProfile) -> None:
    """Set env hints for the detected backend."""
    os.environ["OMP_NUM_THREADS"] = str(profile.workers)
    os.environ["MKL_NUM_THREADS"] = str(profile.workers)

    if profile.backend == "cuda":
        os.environ.pop("CUDA_VISIBLE_DEVICES", None)
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
        if profile.unified_memory:
            os.environ["CUDA_MANAGED_FORCE_DEVICE_ALLOC"] = "0"
    elif profile.backend == "hip":
        os.environ["HSA_OVERRIDE_GFX_VERSION"] = os.environ.get("HSA_OVERRIDE_GFX_VERSION", "")
        os.environ["HIP_VISIBLE_DEVICES"] = ",".join(str(g.index) for g in profile.gpus)
    elif profile.backend == "vulkan":
        os.environ["OLLAMA_VULKAN"] = "1"
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        os.environ["OLLAMA_VULKAN"] = "0"


def optimize_gpu_memory(profile: HardwareProfile) -> dict:
    """Apply GPU memory optimizations for the detected backend."""
    applied = []
    if profile.backend == "cuda":
        try:
            import torch
            torch.cuda.empty_cache()
            # Limit per-process fraction
            for i in range(profile.gpu_count):
                torch.cuda.set_per_process_memory_fraction(profile.gpu_memory_fraction, i)
            applied.append("cuda_fraction")
            applied.append("empty_cache")
        except Exception:
            pass
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:128"
        applied.append("alloc_conf")
    elif profile.backend == "hip":
        os.environ["HSA_ENABLE_SDMA"] = "0"  # reduce copy overhead
        applied.append("hsa_sdma_off")
    elif profile.backend == "vulkan":
        os.environ["OLLAMA_VULKAN"] = "1"
        applied.append("vulkan_on")
    return {"backend": profile.backend, "applied": applied, "fraction": profile.gpu_memory_fraction}
