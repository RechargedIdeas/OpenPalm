"""Backend interface."""

from abc import ABC, abstractmethod
from typing import Any


class Backend(ABC):
    name: str = "base"

    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def device_count(self) -> int: ...

    @abstractmethod
    def info(self) -> dict: ...

    @abstractmethod
    def alloc(self, size: int) -> Any: ...

    @abstractmethod
    def empty_cache(self) -> None: ...

    def set_memory_fraction(self, fraction: float) -> None:
        pass
