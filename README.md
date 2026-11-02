# Agent Harness

A local-first AI assistant for everyone. Built for people who know little or nothing about AI — including older adults, students, artists, musicians, small businesses, schools, nonprofits, scientists, and anyone who finds technology hard to navigate.

Runs on ordinary laptops (8 GB RAM, no dedicated GPU required). Every answer is checked against your own files and notes before you can copy or share it.

## Who it is for

- Someone who wants help writing a letter, a lesson plan, a grant, a song idea, or a research summary
- A small business owner who needs to draft an email or summarize a spreadsheet
- A teacher or nonprofit volunteer who must keep client or student information private
- Anyone who has been burned by AI making things up

## What it does

- Answers questions using the documents and notes you give it
- Shows which statements are supported by your sources and which are not
- Keeps Copy and Share disabled until unsupported claims are fixed
- Runs entirely on your computer by default (CPU-only; no GPU needed)
- Speaks in plain language; no technical settings required

## What it is not

- Not a chatbot that invents facts
- Not a tool that sends your private data to the cloud unless you explicitly choose that and confirm the warning
- Not complicated. Six main areas. One verification slider. One help button.

## Quick start (no GPU required)

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

The server starts automatically if it is not already running. Use Start / Stop / Reset in the header.

## For agents and contributors

- Read `AGENTS.md` first
- See `CONTRIBUTING.md`
- Current priorities are in `TASKS.md`
