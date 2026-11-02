# OpenPalm

A simple, local AI assistant that checks every answer against your own documents before you can copy or share it.

Built for people who know little or nothing about AI — including older adults, students, artists, musicians, small businesses, schools, nonprofits, scientists, and anyone who finds technology hard to navigate.

## Why the name

OpenPalm is the simple, open palm anyone can rest on. It does one thing that matters: it checks claims against the sources you provide. If a statement is not in your files or notes, you cannot copy or share it until you fix it.

## Who it is for

- A musician writing a bio from their own notes
- A teacher summarizing a parent email
- A nonprofit drafting a grant from program documents
- A scientist checking a methods paragraph against lab notes
- An older adult writing a letter to a doctor
- Anyone tired of programs that invent facts

## What it does

- Answers using the documents and notes you give it
- Labels every claim Supported or Unsupported
- Keeps Copy and Share off until unsupported claims are fixed
- Runs on a regular computer (CPU-only; no GPU needed)
- Speaks in plain language

## Quick start

```bash
cd sidecar
pip install -r requirements.txt
python3 gui.py
```

The helper starts automatically if it is not running. Use Start / Stop / Reset in the header.


## Launch options

```bash
cd sidecar
python3 gui.py           # Python GUI
python3 gui.py --web     # React Web GUI (after npm run build)
python3 gui.py --both    # both
```

Both GUIs share chat history, settings, and sources through the server at `http://127.0.0.1:8765/data`.



## Pairing

Desktop generates a short code and QR. Android redeems the code or scans the QR. Tailscale addresses are preferred when available.

- Generate: `GET /pair/code`
- Redeem: `POST /pair/redeem` with `{"code": "XXXXXX"}`
- Status: `GET /pair/status`

## Android

An independent Android app is in `android/`. It works offline and can pair with the desktop server for shared data and remote control.

```bash
# Open android/ in Android Studio, or:
cd android
# (requires Android SDK)
```

See `android/README.md` for pairing and build details.

## Manual

The complete user manual with detailed examples is in `manual/USER-MANUAL.md`.

## For agents and contributors

- Read `AGENTS.md`
- See `CONTRIBUTING.md`
- Current priorities are in `TASKS.md`

## Recent additions

- **Model Management** — hardware-aware catalog of LLMs, vision, audio, video, image, and embedding models with estimated tok/s and Hugging Face download
- **Watchdog** — monitors model output and processes for escape attempts and harmful patterns; learns from alerts and from RAMA feedback
- **RAMA** — local router with parallel states (working, backup, training), self-training, and orchestration of specialists and meta-models
- **Sandbox** — default-on isolation via namespaces; toggle for network, GPU, and direct hardware
- **Training** — background jobs, distillation (response/feature/relation), 20 meta-models, cooperative cancellation
- **Real-time monitor** — SSE stream of logs, training jobs, Watchdog alerts, metrics, hardware, and sandbox
- **Slash commands** — 100+ commands in the terminal and CLI
- **Activity log** — copy and export, with keyboard shortcuts

## Tests

```bash
cd sidecar && python3 tests/test_full_orchestration.py
```

Covers routing, specialists, catalog, meta-models, training, distillation, Watchdog, sandbox, monitor, and a RAMA-orchestrated project build.
