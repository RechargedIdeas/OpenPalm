"""Hot reload: watch modules and reload without dropping state."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any


class HotReloader:
    def __init__(self, packages: list[str] | None = None):
        self.packages = packages or [
            "harness_sidecar.framework",
            "harness_sidecar.framework.models",
            "harness_sidecar.framework.tools",
            "harness_sidecar.framework.skills",
        ]
        self._mtimes: dict[str, float] = {}

    def check(self) -> list[str]:
        """Return list of modules that changed on disk."""
        changed = []
        for pkg in self.packages:
            mod = sys.modules.get(pkg)
            if not mod or not hasattr(mod, "__file__") or not mod.__file__:
                continue
            path = Path(mod.__file__)
            if path.exists():
                mtime = path.stat().st_mtime
                if pkg in self._mtimes and mtime > self._mtimes[pkg]:
                    changed.append(pkg)
                self._mtimes[pkg] = mtime
        return changed

    def reload(self, names: list[str] | None = None) -> list[str]:
        """Reload changed (or specified) modules. Returns reloaded names."""
        targets = names or self.check()
        reloaded = []
        for name in targets:
            if name in sys.modules:
                importlib.reload(sys.modules[name])
                reloaded.append(name)
        return reloaded
