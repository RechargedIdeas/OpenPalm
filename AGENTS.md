# AGENTS.md — Instructions for the AI Builder

You are building Neighbor, agent software for the people. The audience includes older adults, artists, musicians, small businesses, schools, nonprofits, scientists, and anyone who finds technology difficult.

Neighbor is an agent, not a fact-checker product. Verification is a safety feature that keeps the agent honest; it is not the brand.

## Core rules

**Simplicity is the product.** Every control must answer: “Would a non-technical person know why they would change this?”

**The agent stays grounded.** Never let Copy or Share activate while unsupported claims remain.

**Local first / CPU-only by default.** Cloud requires an explicit, warned opt-in.

**No scraping.** Accept only files, notes, CSVs, or licensed APIs the user already has the right to use.

**Maximum six top-level navigation items.**

## How to run

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

See `manual/USER-MANUAL.md` for the full user manual and worked examples.
