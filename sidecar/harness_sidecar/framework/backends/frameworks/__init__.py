"""Training and inference backends for major frameworks."""

from .base import FrameworkBackend
from .pytorch import PyTorchBackend
from .tensorflow import TensorFlowBackend
from .jax_backend import JAXBackend
from .onnx_backend import ONNXBackend
from .numpy_backend import NumPyBackend
from .advanced import TransformerBackend, MoEBackend, LoRABackend

_ALL = {
    "pytorch": PyTorchBackend,
    "tensorflow": TensorFlowBackend,
    "jax": JAXBackend,
    "onnx": ONNXBackend,
    "numpy": NumPyBackend,
    "transformer": TransformerBackend,
    "moe": MoEBackend,
    "lora": LoRABackend,
}

def get_framework(name: str = "auto") -> FrameworkBackend:
    if name == "auto":
        for n in ("pytorch", "tensorflow", "jax", "onnx", "numpy"):
            b = _ALL[n]()
            if b.available():
                return b
        return NumPyBackend()
    cls = _ALL.get(name)
    if not cls:
        raise ValueError(f"unknown framework: {name}")
    return cls()

def list_frameworks() -> dict:
    out = {}
    for name, cls in _ALL.items():
        b = cls()
        out[name] = {"available": b.available(), "train": b.supports_train, "infer": b.supports_infer}
    return out
