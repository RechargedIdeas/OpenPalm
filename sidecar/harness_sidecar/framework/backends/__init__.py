"""Compute backends: CUDA, HIP, CPU."""

from .base import Backend
from .cuda import CUDABackend
from .hip import HIPBackend
from .cpu import CPUBackend

def get_backend(name: str = "auto") -> Backend:
    if name == "cuda":
        return CUDABackend()
    if name == "hip":
        return HIPBackend()
    if name == "cpu":
        return CPUBackend()
    # auto
    c = CUDABackend()
    if c.available():
        return c
    h = HIPBackend()
    if h.available():
        return h
    return CPUBackend()
