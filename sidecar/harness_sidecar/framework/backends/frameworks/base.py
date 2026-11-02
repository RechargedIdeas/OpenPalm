"""Framework backend interface for train and infer."""

from abc import ABC, abstractmethod
from typing import Any


class FrameworkBackend(ABC):
    name: str = "base"
    supports_train: bool = False
    supports_infer: bool = False

    @abstractmethod
    def available(self) -> bool: ...

    @abstractmethod
    def train(self, spec: dict, data: Any = None, epochs: int = 1) -> dict: ...

    @abstractmethod
    def infer(self, model: Any, inputs: Any) -> dict: ...

    def info(self) -> dict:
        return {"name": self.name, "available": self.available()}
