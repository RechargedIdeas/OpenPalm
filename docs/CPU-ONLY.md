# CPU-only mode

Agent Harness runs entirely on the CPU. No GPU is required. This is intentional: the product must work on ordinary laptops used by older adults, students, small nonprofits, and anyone without a gaming PC.

- The sidecar sets `OLLAMA_VULKAN=0` on startup.
- Small models are recommended.
- Drafting, verification, file search, and charts all work; generation is simply slower.

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```
