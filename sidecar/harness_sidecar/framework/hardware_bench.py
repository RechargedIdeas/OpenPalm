"""Auto-benchmark hardware and recommend optimal settings.

Runs short CPU and optional GPU probes, then returns tuned workers/batch.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from .hardware import HardwareProfile, detect


@dataclass
class BenchResult:
    cpu_score: float  # ops/sec
    gpu_score: float
    recommended_workers: int
    recommended_batch: int
    duration_ms: float
    notes: str


def _cpu_work(n: int) -> int:
    """Simple integer workload."""
    s = 0
    for i in range(n):
        s += i * i
    return s


def _bench_cpu(workers: int, iters: int = 200_000) -> float:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_cpu_work, [iters // workers] * workers))
    elapsed = time.perf_counter() - start
    return iters / max(elapsed, 1e-6)


def _bench_gpu() -> float:
    try:
        import torch
        if not torch.cuda.is_available():
            return 0.0
        device = torch.device("cuda")
        a = torch.randn(1024, 1024, device=device)
        b = torch.randn(1024, 1024, device=device)
        torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(10):
            c = a @ b
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - start
        return 10 / max(elapsed, 1e-6)
    except Exception:
        return 0.0


def benchmark(profile: HardwareProfile | None = None) -> BenchResult:
    """Run a short benchmark and recommend settings."""
    prof = profile or detect()
    start = time.perf_counter()

    # Probe a few worker counts
    candidates = sorted(set([
        1,
        max(1, prof.cpu_count // 2),
        prof.cpu_count,
        min(prof.cpu_count * 2, 32),
    ]))
    scores = {}
    for w in candidates:
        scores[w] = _bench_cpu(w)

    best_workers = max(scores, key=scores.get)
    cpu_score = scores[best_workers]

    gpu_score = _bench_gpu() if prof.gpu_count else 0.0

    # Batch: scale with memory and GPU
    if prof.mode == "multi-gpu":
        batch = min(16, max(4, prof.gpu_count * 2))
    elif prof.mode == "single-gpu":
        batch = 4 if prof.memory_gb > 8 else 2
    else:
        batch = 1 if prof.memory_gb < 4 else 2

    # If CPU is weak, stay conservative
    if cpu_score < 1_000_000:
        best_workers = max(1, best_workers // 2)
        batch = 1

    duration = (time.perf_counter() - start) * 1000
    notes = f"tested workers {candidates}; best {best_workers} ({cpu_score:.0f} ops/s)"
    if gpu_score:
        notes += f"; gpu {gpu_score:.1f} matmul/s"

    return BenchResult(
        cpu_score=round(cpu_score, 1),
        gpu_score=round(gpu_score, 2),
        recommended_workers=best_workers,
        recommended_batch=batch,
        duration_ms=round(duration, 1),
        notes=notes,
    )


def apply_bench(result: BenchResult) -> None:
    """Push recommended settings into env."""
    import os
    os.environ["OMP_NUM_THREADS"] = str(result.recommended_workers)
    os.environ["MKL_NUM_THREADS"] = str(result.recommended_workers)
