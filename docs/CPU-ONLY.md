# CPU-only mode

Agent Harness runs entirely on the CPU. No GPU is required.

On machines without a dedicated GPU (including 8 GB Intel iGPU laptops):

- Set `OLLAMA_VULKAN=0` (done automatically by the sidecar on startup).
- Use a small model such as Phi-4-mini or Qwen3 1.7B.
- Everything (drafting, verification, RAG search, charts, bots) works; generation is simply slower.

## Verified working path (no GPU)

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

Or start the server directly:

```bash
python3 -m uvicorn harness_sidecar.api.server:app --host 127.0.0.1 --port 8765
```

The GUI header has Start / Stop / Reset. The server auto-starts if it is not already running.
