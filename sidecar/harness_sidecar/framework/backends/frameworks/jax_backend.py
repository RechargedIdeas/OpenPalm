"""JAX train and infer backend."""

from typing import Any
from .base import FrameworkBackend


class JAXBackend(FrameworkBackend):
    name = "jax"
    supports_train = True
    supports_infer = True

    def available(self) -> bool:
        try:
            import jax
            return True
        except Exception:
            return False

    def train(self, spec: dict, data: Any = None, epochs: int = 1) -> dict:
        if not self.available():
            return {"ok": False, "error": "jax not installed"}
        import jax
        import jax.numpy as jnp
        key = jax.random.PRNGKey(0)
        w = jax.random.normal(key, (4, 1))
        x = jax.random.normal(key, (8, 4))
        y = jax.random.normal(key, (8, 1))
        def loss(w, x, y):
            return jnp.mean((x @ w - y) ** 2)
        grad = jax.grad(loss)
        for _ in range(epochs):
            w = w - 0.01 * grad(w, x, y)
        return {"ok": True, "framework": "jax", "epochs": epochs, "final_loss": float(loss(w, x, y))}

    def infer(self, model: Any, inputs: Any) -> dict:
        if not self.available():
            return {"ok": False, "error": "jax not installed"}
        import jax.numpy as jnp
        w = model if model is not None else jnp.zeros((4, 1))
        x = jnp.array(inputs)
        return {"ok": True, "framework": "jax", "output": (x @ w).tolist()}
