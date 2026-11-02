# PLAN.md — Build Roadmap

Ten phases. Each ends with a checkpoint that requires human review. Ship a
demoable shell by Phase 6, then add intelligence.

## Phase 0 — Repository setup (0.5 day)

**Deliverables:**
- Tauri v2 + React 19 + TypeScript + Vite 7 project scaffolded
- shadcn/ui installed and one component rendered as proof
- Directory structure: `src/` (frontend), `src-tauri/` (Rust), `sidecar/` (Python)
- `.gitignore` covering `node_modules`, `target`, `*.gguf`, `.env`
- README, AGENTS, PLAN, TODO, and docs/ files committed
- CI stub that runs `pnpm lint`, `pnpm typecheck`, `cargo check`

**Acceptance:** `pnpm tauri dev` opens a window with a hello-world React component.

## Phase 1 — Shell and navigation (3 days)

**Deliverables:**
- Three-panel layout: left sidebar (220px, collapsible), main work area, no bottom bar yet
- Six sidebar items: Chat, Files, Email, MLS/CSV, Charts, Settings
- Top bar: hamburger, app name, model selector (stub), search, settings, help
- Preferences persistence (window size, sidebar state, theme)
- Empty states for each main view with a one-line explanation and a "Read the guide" link

**Acceptance:** Sidebar collapses and expands; state persists across restart; navigating between views shows the correct empty state; UI works at 1920x1080 and 1280x720.

**Demoable:** Yes. This is the first checkpoint where a human can see the product.

## Phase 2 — Chat and verification table (4 days)

**Deliverables:**
- Chat input with streaming response rendering
- Inline tool-call chips in the agent's response stream
- Verification table component: collapsible, color-coded claims, Fix button on unsupported items
- Copy and Send buttons disabled while unsupported claims exist
- Verification pass slider (Fast 1 / Standard 2 / Strict 3) with plain-text explanation
- Sidecar stub that returns hardcoded drafts and audits (no real model yet)

**Acceptance:** Chat renders a streamed response; verification table expands and collapses; copy button stays disabled when a hardcoded unsupported claim is present; slider changes the displayed pass count and the stub returns a different audit length.

**Demoable:** Yes. The verification concept is visible without any model.

## Phase 3 — Bottom bar (3 days)

**Deliverables:**
- Resizable bottom panel: default 220px, draggable 80px–60% of window height
- Three tabs: Terminal, Activity Log, Debug
- Terminal: xterm.js + tauri-pty, correct resize sync (clamped min 2 cols, 3 rows), `TERM=xterm-256color`, `COLORTERM=truecolor`, WebGL renderer with canvas fallback
- Activity Log: structured human-readable event stream wired to the Rust logger
- Debug: raw JSON-RPC and tool payloads, hidden behind a Settings toggle
- Collapse button moves the whole panel to a single top-bar toggle
- Maximize button fills the window below the top bar; chat is hidden but not unmounted
- Collapse state and height persist across restart

**Acceptance:** Terminal resize at any window dimension produces no text corruption; switching tabs does not kill the PTY session; collapse and restore preserves the previous height; maximize and restore preserves chat scroll position.

**Demoable:** Yes. Terminal runs `echo hello` and accepts input.

## Phase 4 — Slash commands (2 days)

**Deliverables:**
- Command registry in `src/lib/commands.ts`
- Inline picker on `/`: keyboard-navigable, prefix-filtered, Esc dismisses, Enter or Tab commits
- Argument hint insertion for commands that take arguments (`/model`, `/facts`)
- Commands: `/help`, `/clear`, `/model`, `/facts`, `/files`, `/email`, `/sync`, `/status`, `/logs`, `/debug`, `/exit`
- `/help` opens the manual to the relevant section (manual ships in Phase 6; stub for now)

**Acceptance:** Every command executes its action; `/model` opens the model picker; `/facts 3` updates the slider; `/status` prints model, memory, index size, and verification level to the Terminal tab; `/help` opens the manual overlay to the correct chapter.

## Phase 5 — MCP client and server (4 days)

**Deliverables:**
- MCP client in the Python sidecar (official MCP Python SDK)
- Connectors page under Settings with curated cards: Filesystem, Email, Google Calendar, MLS/CSV
- Each card has a status dot, a toggle, and an "Add" button
- MCP server: harness exposes `search_files`, `query_mls`, `read_email`, `draft_listing`, `run_verification` as tools
- Elicitation wired to the standard confirmation dialog for write actions
- Share toggle in Settings displays the SSE endpoint and copy button; off by default
- Local HTTP API on `127.0.0.1` with bearer token; token generated on first run, masked in UI, regenerate button

**Acceptance:** Connect the filesystem MCP server and call `search_files` from chat; connect the harness to Claude Desktop via the SSE endpoint and call `run_verification`; attempting a network-bound API exposure shows the warned opt-in dialog.

## Phase 6 — Embedded manual (3 days)

**Deliverables:**
- Manual authored in Markdown under `manual/` with the twelve chapters from the spec
- In-app viewer: full-screen overlay, table of contents, search via MiniSearch
- Four access points: top-bar Help button, `/help` command, contextual "?" icons, empty states
- Troubleshooting chapter written as numbered diagnostic steps using `/status` and `/logs`
- "Was this helpful?" footer logs feedback to Activity Log

**Acceptance:** Search finds any chapter by keyword; `/help` opens the correct chapter based on context; every "?" icon deep-links to the right page; troubleshooting steps can be followed inside the Terminal tab without leaving the app.

**Demoable:** Yes. This is the end of the shell-only build. A human reviewer can now evaluate the entire product concept without any AI running.

## Phase 7 — Hardware probe, model recommendation, RAG (5 days)

**Deliverables:**
- Hardware probe module (Rust): CPU vendor, cores, AVX flags, RAM, GPU, VRAM, disk, Ollama presence
- Recommendation engine reusing `ollama-advisor` logic or reimplementing the scoring
- Three-card UI with model name, params, tokens/sec, RAM footprint, one-sentence plain explanation
- One-click download via Ollama with progress, followed by automatic 20-token generation test
- RAG pipeline in the sidecar: SQLite vector store, `nomic-embed-text` via Ollama, chunking by document type
- File ingestion UI: "Add folder" button, supported-format list, OCR step for scans

**Acceptance:** On the low-spec simulation, the probe recommends Phi-4-mini, download succeeds, self-test passes, and a PDF dropped into a watched folder becomes searchable within 30 seconds.

## Phase 8 — Email, MLS, charts, bots, workflows (5 days)

**Deliverables:**
- Email connector via MCP email server (Gmail, Outlook, manual IMAP)
- Local SQLite email index; bodies never leave the machine on local backend
- MLS CSV upload UI; query interface with column-aware suggestions
- Chart tool: bar, line, scatter, export to PNG
- Bot creation wizard: name, tool subset, system prompt, optional schedule
- Workflow DAG editor (basic): trigger, steps, approval gates
- Skills system: markdown packs for listing writer, CMA narrative, objection rehearsal, compliance review

**Acceptance:** Connect Gmail, search for a subject line, get results; upload an MLS CSV, ask "sort by sqft and flag outliers," get a sorted table; create a seller follow-up bot that drafts an email; the compliance review skill flags "must-see" in a draft.

## Phase 9 — Hardening and low-spec validation (3 days)

**Deliverables:**
- Full low-spec simulation: 8 GB RAM cap, Phi-4-mini only, run a full chat-verify-send cycle
- Memory profile: no leaks over a 30-minute session
- Cold start time measured and documented
- Signed installers for Windows and macOS
- Crash recovery: unsaved chat restored on relaunch
- Security review: prompt injection boundary tested with a hostile email, confirmation gate tested with a hostile document

**Acceptance:** Full cycle under 4 GB RSS on the low-spec simulation; hostile email does not trigger a tool call without confirmation; installer runs on a clean VM and reaches first chat within 90 seconds.

## Summary timeline

| Phase | Days | Cumulative |
|---|---|---|
| 0 | 0.5 | 0.5 |
| 1 | 3 | 3.5 |
| 2 | 4 | 7.5 |
| 3 | 3 | 10.5 |
| 4 | 2 | 12.5 |
| 5 | 4 | 16.5 |
| 6 | 3 | 19.5 |
| 7 | 5 | 24.5 |
| 8 | 5 | 29.5 |
| 9 | 3 | 32.5 |

Estimate assumes one competent AI builder with human review at each checkpoint.
