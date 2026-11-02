"""NumPy fallback train and infer backend. Always available."""

from typing import Any
from .base import FrameworkBackend


class NumPyBackend(FrameworkBackend):
    name = "numpy"
    supports_train = True
    supports_infer = True

    def available(self) -> bool:
        return True

    def train(self, spec: dict, data: Any = None, epochs: int = 1) -> dict:
        # Simulate a tiny linear fit
        loss = 1.0
        for i in range(epochs):
            loss *= 0.9
        return {"ok": True, "framework": "numpy", "epochs": epochs, "final_loss": round(loss, 4)}

    def infer(self, model: Any, inputs: Any) -> dict:
        # Echo-style stub
        if isinstance(inputs, list):
            out = [float(sum(row)) if isinstance(row, list) else float(row) for row in inputs]
        else:
            out = [0.0]
        return {"ok": True, "framework": "numpy", "output": out}
