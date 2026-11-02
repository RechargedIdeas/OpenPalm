# Contributing

Maintained by humans and AI agents.

## Quick start

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

## Server management

| Action | How |
|---|---|
| Start | python3 sidecar/gui.py or POST /control/start |
| Stop | Header button or POST /control/stop |
| Reset | Header button or POST /control/reset |
| Status | GET /control/status or GET /health |

## Workflow

1. Branch from main
2. Make focused changes
3. Run python3 tests/test_stubs.py if available
4. Open a pull request describing what changed and how you tested it

## Rules

- Verification cannot be turned off
- Default is local / CPU-only
- No listing-portal scrapers
- Max six top-level nav items
- Do not commit secrets or model weights
