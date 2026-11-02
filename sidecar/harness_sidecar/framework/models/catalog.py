"""Hardware-aware model catalog.

Lists models by type with estimated tokens/sec, VRAM needs, and best uses.
"""

from __future__ import annotations

from typing import Any


CATALOG = [
    # LLMs
    {"id": "phi4-mini", "hf": "microsoft/Phi-4-mini-instruct", "name": "Phi-4 Mini", "type": "llm", "params": "3.8B", "vram_gb": 3, "tps_cpu": 8, "tps_gpu": 45, "uses": ["chat", "summarize", "local assistant"], "license": "MIT"},
    {"id": "llama-3.2-1b", "hf": "meta-llama/Llama-3.2-1B", "name": "Llama 3.2 1B", "type": "llm", "params": "1B", "vram_gb": 1.5, "tps_cpu": 15, "tps_gpu": 80, "uses": ["fast chat", "routing"], "license": "Llama"},
    {"id": "llama-3.2-3b", "name": "Llama 3.2 3B", "type": "llm", "params": "3B", "vram_gb": 2.5, "tps_cpu": 6, "tps_gpu": 40, "uses": ["general", "code"], "license": "Llama"},
    {"id": "qwen2.5-7b", "name": "Qwen2.5 7B", "type": "llm", "params": "7B", "vram_gb": 5, "tps_cpu": 2, "tps_gpu": 25, "uses": ["reasoning", "multilingual"], "license": "Apache-2.0"},
    {"id": "mistral-7b", "name": "Mistral 7B", "type": "llm", "params": "7B", "vram_gb": 5, "tps_cpu": 2, "tps_gpu": 28, "uses": ["instruction", "chat"], "license": "Apache-2.0"},
    {"id": "gemma-2-2b", "name": "Gemma 2 2B", "type": "llm", "params": "2B", "vram_gb": 2, "tps_cpu": 10, "tps_gpu": 55, "uses": ["edge", "fast reply"], "license": "Gemma"},
    # Vision
    {"id": "clip-vit-b", "name": "CLIP ViT-B/32", "type": "vision", "params": "150M", "vram_gb": 0.5, "tps_cpu": 20, "tps_gpu": 120, "uses": ["image search", "zero-shot class"], "license": "MIT"},
    {"id": "yolo-v8n", "name": "YOLOv8 Nano", "type": "vision", "params": "3M", "vram_gb": 0.3, "tps_cpu": 15, "tps_gpu": 200, "uses": ["object detect", "realtime"], "license": "AGPL"},
    {"id": "sam-vit-b", "name": "SAM ViT-B", "type": "vision", "params": "90M", "vram_gb": 1, "tps_cpu": 2, "tps_gpu": 15, "uses": ["segmentation"], "license": "Apache-2.0"},
    {"id": "llava-7b", "name": "LLaVA 7B", "type": "vision", "params": "7B", "vram_gb": 6, "tps_cpu": 1, "tps_gpu": 12, "uses": ["image chat", "caption"], "license": "Llama"},
    # Audio
    {"id": "whisper-tiny", "hf": "openai/whisper-tiny", "name": "Whisper Tiny", "type": "audio", "params": "39M", "vram_gb": 0.2, "tps_cpu": 30, "tps_gpu": 150, "uses": ["transcribe", "fast"], "license": "MIT"},
    {"id": "whisper-base", "name": "Whisper Base", "type": "audio", "params": "74M", "vram_gb": 0.4, "tps_cpu": 12, "tps_gpu": 60, "uses": ["transcribe", "accurate"], "license": "MIT"},
    {"id": "bark-small", "name": "Bark Small", "type": "audio", "params": "80M", "vram_gb": 1, "tps_cpu": 1, "tps_gpu": 8, "uses": ["tts", "voice"], "license": "MIT"},
    # Video
    {"id": "svd-xt", "name": "Stable Video Diffusion", "type": "video", "params": "1.5B", "vram_gb": 8, "tps_cpu": 0.01, "tps_gpu": 0.5, "uses": ["image-to-video"], "license": "research"},
    {"id": "animatediff", "name": "AnimateDiff", "type": "video", "params": "1B", "vram_gb": 6, "tps_cpu": 0.02, "tps_gpu": 1, "uses": ["text-to-video", "motion"], "license": "Apache-2.0"},
    # Image gen
    {"id": "sd-1.5", "name": "Stable Diffusion 1.5", "type": "image", "params": "0.9B", "vram_gb": 4, "tps_cpu": 0.05, "tps_gpu": 2, "uses": ["text-to-image"], "license": "CreativeML"},
    {"id": "sdxl", "name": "SDXL", "type": "image", "params": "3.5B", "vram_gb": 8, "tps_cpu": 0.01, "tps_gpu": 0.8, "uses": ["high-res image"], "license": "OpenRAIL"},
    {"id": "flux-schnell", "name": "Flux Schnell", "type": "image", "params": "12B", "vram_gb": 12, "tps_cpu": 0, "tps_gpu": 0.3, "uses": ["fast image"], "license": "Apache-2.0"},
    # Embeddings
    {"id": "bge-small", "hf": "BAAI/bge-small-en-v1.5", "name": "BGE Small", "type": "embedding", "params": "33M", "vram_gb": 0.2, "tps_cpu": 100, "tps_gpu": 500, "uses": ["RAG", "search"], "license": "MIT"},
    {"id": "nomic-embed", "name": "Nomic Embed", "type": "embedding", "params": "137M", "vram_gb": 0.5, "tps_cpu": 40, "tps_gpu": 200, "uses": ["RAG", "long context"], "license": "Apache-2.0"},
]


def fit(model: dict, ram_gb: float, vram_gb: float, has_gpu: bool) -> dict:
    """Score how well a model fits the hardware."""
    need = model["vram_gb"]
    if has_gpu and vram_gb >= need:
        status = "gpu"
        tps = model["tps_gpu"]
    elif ram_gb >= need * 1.5:
        status = "cpu"
        tps = model["tps_cpu"]
    else:
        status = "too-big"
        tps = 0
    return {**model, "fit": status, "est_tps": tps}


def catalog_for(ram_gb: float = 8, vram_gb: float = 0, has_gpu: bool = False, type_filter: str | None = None) -> list[dict]:
    items = CATALOG if not type_filter else [m for m in CATALOG if m["type"] == type_filter]
    return [fit(m, ram_gb, vram_gb, has_gpu) for m in items]


def types() -> list[str]:
    return sorted({m["type"] for m in CATALOG})
