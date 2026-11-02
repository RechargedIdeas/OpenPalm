# Contributing to Neighbor

Neighbor is agent software for everyone. It is maintained by humans and AI agents.

## Quick start

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

## Server management

| Action | How |
|---|---|
| Start | `python3 sidecar/gui.py` or `POST /control/start` |
| Stop | Header button or `POST /control/stop` |
| Reset | Header button or `POST /control/reset` |
| Status | `GET /control/status` or `GET /health` |

## Rules

- Neighbor is an agent for the people, not a fact-checker brand
- Verification cannot be turned off
- Default is local / CPU-only
- No scrapers
- Maximum six top-level navigation items
- Plain language in the UI
- Do not commit secrets or model weights

## Manual

Full user manual with detailed examples: `manual/USER-MANUAL.md`
