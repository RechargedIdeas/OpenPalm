# AGENTS.md — Instructions for the AI Builder

You are building OpenPalm, a desktop application for people who know little or nothing about AI. The audience includes older adults, artists, musicians, small businesses, schools, nonprofits, scientists, and anyone who finds technology difficult.

The product name is OpenPalm. The core promise is that every factual claim is checked against the user’s own sources before Copy or Share is allowed.

## Reading order

1. This file
2. PLAN.md
3. docs/ARCHITECTURE.md
4. manual/USER-MANUAL.md
5. TASKS.md
6. docs/ACCEPTANCE.md

## Core rules

**Simplicity is the product.** Every control must answer: “Would a non-technical person know why they would change this?”

**Verification is not optional.** Never let Copy or Share activate while unsupported claims remain.

**Local first / CPU-only by default.** Cloud requires an explicit, warned opt-in.

**No scraping.** Accept only files, notes, CSVs, or licensed APIs the user already has the right to use.

**Maximum six top-level navigation items.**

## Audience examples

See manual/USER-MANUAL.md section 7 for full worked examples (musician, artist, small business, teacher, nonprofit, scientist, older adult).

## How to run

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

## Stop-and-ask conditions

Stop and ask before adding a seventh nav item, a write action without confirmation, a change to the verification default, a new cloud provider, or a longer onboarding flow.
