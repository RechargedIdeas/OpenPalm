# AGENTS.md — Instructions for the AI Builder

You are building Agent Harness, a desktop AI application for non-technical real estate agents. Read this fully before touching code.

## Reading order

1. This file
2. PLAN.md
3. docs/ARCHITECTURE.md
4. docs/CONVENTIONS.md
5. TASKS.md (current priorities)
6. docs/ACCEPTANCE.md

## Core rules

- Verification is not optional. Never let Copy/Send activate while unsupported claims remain.
- Local first / CPU-only by default. Cloud requires an explicit warned opt-in.
- No portal scraping. Accept only user-provided CSVs or licensed APIs.
- Maximum six top-level navigation items.
- Simplicity is the product. The target user is a licensed agent, not a developer.

## How to run

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

Server auto-starts if not running. Start / Stop / Reset are in the GUI header.

## Contribution

See CONTRIBUTING.md. Update TASKS.md or add a note in docs/checkpoints/ when you finish work.
