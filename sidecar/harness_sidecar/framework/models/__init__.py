"""Specialist model registry and router.

Each specialist is a thin adapter over the base generate() function
with domain prompts, validation, and fallback behavior.
"""

from .registry import ModelRegistry, Specialist
from .router import ModelRouter

__all__ = ["ModelRegistry", "Specialist", "ModelRouter"]
