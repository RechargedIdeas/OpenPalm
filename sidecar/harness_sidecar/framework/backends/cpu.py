"""CPU backend."""

from typing import Any
from .base import Backend


class CPUBackend(Backend):
    name = "cpu"

    def available(self) -> bool:
        return True

    def device_count(self) -> int:
        import os
        return os.cpu_count() or 1

    def info(self) -> dict:
        return {"available": True, "cores": self.device_count()}

    def alloc(self, size: int) -> Any:
        return bytearray(size)

    def empty_cache(self) -> None:
        pass
