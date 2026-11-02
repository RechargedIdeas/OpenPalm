# AGENTS.md — Instructions for the AI Builder

You are building Agent Harness, a desktop AI application for people who know little or nothing about AI. The audience includes older adults, artists, musicians, small businesses, schools, nonprofits, scientists, and anyone who finds technology difficult. Read this fully before touching code.

## Core rules

**Simplicity is the product.** Every control must answer: “Would a non-technical person know why they would change this?”

**Verification is not optional.** Never let Copy or Share activate while unsupported claims remain.

**Local first / CPU-only by default.** Cloud requires an explicit, warned opt-in.

**No scraping.** Accept only files, notes, CSVs, or licensed APIs the user already has the right to use.

**Maximum six top-level navigation items.**

## Audience examples

- Musician drafting a press bio from their own notes
- Teacher summarizing a parent email
- Nonprofit writing a grant from their program documents
- Scientist checking a methods paragraph against their lab notes
- Older adult writing a letter to a doctor or a family member

The verification and privacy rules are the same for every audience.

## How to run

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```
