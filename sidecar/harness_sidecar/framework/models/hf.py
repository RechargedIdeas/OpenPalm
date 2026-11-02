"""Hugging Face model downloader.

Uses huggingface_hub when available; falls back to a direct HTTP fetch of the
resolve URL for small files.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


CACHE = Path(os.environ.get("HF_HOME", "/tmp/hf-models"))


def download(repo: str, filename: str | None = None, revision: str = "main") -> dict:
    """Download a model or file from Hugging Face.

    repo: "org/name"
    filename: optional single file; if omitted, snapshots the repo.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    try:
        from huggingface_hub import hf_hub_download, snapshot_download
        if filename:
            path = hf_hub_download(repo_id=repo, filename=filename, revision=revision, cache_dir=str(CACHE))
        else:
            path = snapshot_download(repo_id=repo, revision=revision, cache_dir=str(CACHE))
        return {"ok": True, "repo": repo, "path": path, "backend": "huggingface_hub"}
    except ImportError:
        pass
    except Exception as e:
        return {"ok": False, "error": str(e), "repo": repo}

    # Fallback: direct GET of a single file
    if not filename:
        return {"ok": False, "error": "huggingface_hub not installed; pass filename for direct download", "repo": repo}
    import urllib.request
    url = f"https://huggingface.co/{repo}/resolve/{revision}/{filename}"
    dest = CACHE / repo.replace("/", "_") / filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        urllib.request.urlretrieve(url, dest)
        return {"ok": True, "repo": repo, "path": str(dest), "backend": "http"}
    except Exception as e:
        return {"ok": False, "error": str(e), "repo": repo, "url": url}


def list_cached() -> list[str]:
    if not CACHE.exists():
        return []
    return [p.name for p in CACHE.iterdir()]
