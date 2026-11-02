"""ONNX Runtime inference backend (no training)."""

from typing import Any
from .base import FrameworkBackend


class ONNXBackend(FrameworkBackend):
    name = "onnx"
    supports_train = False
    supports_infer = True

    def available(self) -> bool:
        try:
            import onnxruntime
            return True
        except Exception:
            return False

    def train(self, spec: dict, data: Any = None, epochs: int = 1) -> dict:
        return {"ok": False, "error": "onnx is inference-only"}

    def infer(self, model: Any, inputs: Any) -> dict:
        if not self.available():
            return {"ok": False, "error": "onnxruntime not installed"}
        return {"ok": True, "framework": "onnx", "output": "(session required)", "note": "pass an InferenceSession as model"}
