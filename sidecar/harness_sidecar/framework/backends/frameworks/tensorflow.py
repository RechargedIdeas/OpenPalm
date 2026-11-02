"""TensorFlow train and infer backend."""

from typing import Any
from .base import FrameworkBackend


class TensorFlowBackend(FrameworkBackend):
    name = "tensorflow"
    supports_train = True
    supports_infer = True

    def available(self) -> bool:
        try:
            import tensorflow as tf
            return True
        except Exception:
            return False

    def train(self, spec: dict, data: Any = None, epochs: int = 1) -> dict:
        if not self.available():
            return {"ok": False, "error": "tensorflow not installed"}
        import tensorflow as tf
        model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(4,))])
        model.compile(optimizer="sgd", loss="mse")
        import numpy as np
        x = np.random.randn(8, 4).astype("float32")
        y = np.random.randn(8, 1).astype("float32")
        hist = model.fit(x, y, epochs=epochs, verbose=0)
        return {"ok": True, "framework": "tensorflow", "epochs": epochs, "final_loss": float(hist.history["loss"][-1])}

    def infer(self, model: Any, inputs: Any) -> dict:
        if not self.available():
            return {"ok": False, "error": "tensorflow not installed"}
        import tensorflow as tf
        import numpy as np
        if model is None:
            model = tf.keras.Sequential([tf.keras.layers.Dense(1, input_shape=(4,))])
        x = np.array(inputs, dtype="float32")
        out = model.predict(x, verbose=0)
        return {"ok": True, "framework": "tensorflow", "output": out.tolist()}
