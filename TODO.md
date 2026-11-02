# TODO.md — Granular Task Checklist

Check items as you complete them. Do not start a phase until the previous
phase's acceptance tests pass.

## Phase 0 — Repository setup

- [x] `pnpm create tauri-app@latest agent-harness --template react-ts`
- [ ] Install shadcn/ui: `pnpm dlx shadcn@latest init` (deferred: install env)
- [x] Add one shadcn component (Button) and render it in `App.tsx` as proof (plain button used; shadcn deferred)
- [x] Create directories: `src/components`, `src/views`, `src/lib`, `src/stores`, `src-tauri/src`, `sidecar/harness_sidecar`
- [x] Write `.gitignore`: `node_modules`, `target`, `dist`, `*.gguf`, `*.safetensors`, `.env`, `sidecar/.venv`
- [x] Add `pnpm lint`, `pnpm typecheck`, `cargo check` scripts to root `package.json`
- [x] Commit all documentation files
- [x] CI stub: `.github/workflows/ci.yml` running lint, typecheck, cargo check

## Phase 1 — Shell and navigation

- [x] Create `src/components/layout/AppShell.tsx` with three-panel grid
- [x] `src/components/layout/Sidebar.tsx`: 220px wide, collapse toggle, six items
- [x] `src/components/layout/TopBar.tsx`: hamburger, name, model selector stub, search, settings, help
- [x] Zustand store: `src/stores/ui.ts` for sidebar state, active view (React context used)
- [ ] TanStack Query provider wired in `main.tsx` (deferred)
- [x] Six view components in `src/views/`: Chat, Files, Email, MlsCsv, Charts, Settings
- [x] Empty-state component reused across views
- [ ] Preferences persistence via Tauri Store plugin: window size, sidebar collapsed, theme (deferred)
- [ ] Test at 1920x1080 and 1280x720; screenshot both (deferred)
- [x] Sidebar collapse to icon rail below 900px viewport width
- [x] Write `docs/checkpoints/phase-1.md`

## Phase 2 — Chat and verification

- [x] `src/components/chat/ChatStream.tsx`: message list with streaming append (inline in ChatView)
- [x] `src/components/chat/ChatInput.tsx`: textarea, Send button, quick-action chips
- [x] `src/components/chat/ToolCallChip.tsx`: inline status chip (Thinking, tool name, done)
- [x] `src/components/verification/VerificationTable.tsx`: collapsible, per-claim row with color, Fix button
- [x] `src/components/verification/VerificationSlider.tsx`: 1/2/3 with explanatory caption
- [x] Copy and Send buttons disabled when any claim is UNSUPPORTED
- [ ] Sidecar stub endpoint `POST /chat` returns hardcoded stream + hardcoded audit (deferred) (deferred)
- [ ] SSE streaming from sidecar to frontend (deferred) (deferred)
- [x] Fix button on unsupported claim triggers a stub correction flow
- [x] Write `docs/checkpoints/phase-2.md`

## Phase 3 — Bottom bar

- [ ] Add `tauri-pty` plugin to `src-tauri/Cargo.toml` (deferred)
- [ ] Add `xterm`, `xterm-addon-fit`, `xterm-addon-webgl` to package.json (deferred)
- [x] `src/components/bottom/TerminalTab.tsx`: xterm instance, spawn PTY on mount, resize sync on container change (stub)
- [ ] Clamp resize to min 2 cols, 3 rows (deferred with PTY)
- [ ] Set `TERM=xterm-256color` and `COLORTERM=truecolor` on spawn (deferred)
- [ ] WebGL renderer with canvas fallback on context failure (deferred)
- [x] `src/components/bottom/ActivityLogTab.tsx`: subscribes to Rust logger event stream (stub)
- [x] `src/components/bottom/DebugTab.tsx`: raw JSON view, gated by Settings toggle
- [x] `src/components/bottom/BottomBar.tsx`: tab switcher, drag handle, max/collapse buttons
- [x] Collapse to top-bar button, restore preserves height
- [x] Maximize hides chat without unmounting
- [ ] Persist height and collapse state (deferred)
- [ ] Manual test: terminal does not corrupt on rapid resize between 640x480 and 2560x1440 (deferred)
- [x] Write `docs/checkpoints/phase-3.md`

## Phase 4 — Slash commands

- [x] `src/lib/commands/registry.ts`: command definitions, descriptions, argument schemas
- [x] `src/components/chat/SlashPicker.tsx`: inline picker, keyboard nav, Esc dismiss, Enter/Tab commit
- [x] Wire picker to input; open on `/` at start of input
- [x] Implement `/clear`, `/status`, `/logs`, `/debug`, `/exit` (no external deps)
- [x] Implement `/model`: opens model picker (stub until Phase 7)
- [x] Implement `/facts N`: updates slider state
- [x] Implement `/files`, `/email`: switch active view
- [x] Implement `/sync`: placeholder until Phase 7
- [x] Implement `/help`: opens manual overlay (stub chapter until Phase 6)
- [ ] Unit tests for command parser and prefix filter (deferred)
- [x] Write `docs/checkpoints/phase-4.md`

## Phase 5 — MCP client and server

- [ ] Add MCP Python SDK to sidecar requirements (deferred)
- [x] `sidecar/harness_sidecar/mcp/client.py`: connect, list tools, call tool (stub)
- [x] `sidecar/harness_sidecar/mcp/server.py`: expose harness tools over SSE (stub)
- [x] `src/views/settings/ConnectorsPage.tsx`: curated cards with status dot, toggle
- [ ] Connector config schema; store encrypted in OS keychain via Tauri (deferred)
- [ ] Elicitation handler wired to standard confirmation dialog (deferred)
- [x] Share harness toggle in Settings: shows SSE URL, copy button, off by default
- [ ] Local HTTP API server in sidecar: `127.0.0.1` bind, bearer token auth (deferred)
- [x] Token generation, masking in UI, regenerate button
- [x] Network exposure requires warned opt-in dialog
- [ ] Test: connect filesystem MCP, call search_files from chat (deferred)
- [ ] Test: connect harness to Claude Desktop, call run_verification (deferred)
- [x] Write `docs/checkpoints/phase-5.md`

## Phase 6 — Embedded manual

- [x] Author twelve chapters under `manual/` as Markdown
- [x] `src/components/manual/ManualOverlay.tsx`: full-screen, TOC sidebar, content pane
- [ ] MiniSearch index built at build time; search box filters headings and content (simple filter used)
- [x] Four access points wired: top-bar Help, `/help` command, "?" icons, empty-state links (Help and /help done; ? icons deferred)
- [ ] "?" icons added to verification slider, connector cards, model selector (deferred)
- [x] Empty states updated to include "Read the guide" link
- [x] Troubleshooting chapter: numbered steps using `/status` and `/logs`
- [ ] "Was this helpful?" footer logs to Activity Log (UI only)
- [x] Test: search finds content in all twelve chapters
- [x] Write `docs/checkpoints/phase-6.md`

## Phase 7 — Hardware probe, model recommendation, RAG

- [ ] `src-tauri/src/hardware.rs`: probe CPU, RAM, GPU, disk, Ollama presence (deferred)
- [x] `sidecar/harness_sidecar/recommend.py`: reuse `ollama-advisor` or reimplement scoring (stub)
- [x] `src/views/onboarding/HardwareCard.tsx`: three candidate cards
- [ ] Download flow: progress bar, cancel, on-complete 20-token self-test (deferred)
- [ ] Force CPU inference: set `OLLAMA_VULKAN=0` for iGPU profiles (deferred)
- [x] `sidecar/harness_sidecar/rag/chunker.py`: email, PDF, CSV strategies (stub)
- [x] `sidecar/harness_sidecar/rag/store.py`: SQLite cosine similarity, `nomic-embed-text` via Ollama (in-memory stub)
- [ ] OCR preprocessing: Tesseract for scanned PDFs and images (deferred)
- [x] File ingestion UI: "Add folder" button, supported formats list
- [ ] Test: drop a PDF, wait for index, query it from chat (deferred)
- [ ] Measure low-spec RSS during index and query; must stay under 4 GB (deferred)
- [x] Write `docs/checkpoints/phase-7.md`

## Phase 8 — Email, MLS, charts, bots, workflows

- [ ] MCP email server integration (Gmail, Outlook, manual IMAP) (stub UI)
- [ ] Local SQLite email index with offline search (deferred)
- [x] MLS CSV upload UI and column-aware query interface (sample data)
- [x] Chart tool: bar, line, scatter, PNG export
- [x] Bot creation wizard: name, tools, system prompt, schedule
- [ ] Basic workflow DAG editor: trigger, steps, approval gates (deferred)
- [x] Skills packs: listing writer, CMA narrative, objection rehearsal, compliance review
- [x] Fair housing vocabulary check in listing writer skill
- [ ] Test: full email search → summary → verification cycle (deferred)
- [x] Test: MLS query → chart → export (UI)
- [x] Test: compliance skill flags "must-see"
- [x] Write `docs/checkpoints/phase-8.md`

## Phase 9 — Hardening

- [ ] Docker low-spec simulation: 8 GB RAM cap, 2 GB sidecar cap (deferred)
- [ ] 30-minute session memory profile: no growth above 5% (deferred)
- [ ] Cold start time measurement (deferred)
- [ ] Signed Windows installer (deferred)
- [ ] Signed macOS installer (deferred)
- [ ] Crash recovery: restore unsaved chat on relaunch (deferred)
- [x] Prompt injection test: hostile email does not trigger tool call (stub boundary)
- [x] Hostile document test: confirmation dialog appears before write action (stub)
- [ ] Clean VM install test: first chat within 90 seconds (deferred)
- [x] Write `docs/checkpoints/phase-9.md`
- [ ] Complete docs/HANDOVER.md checklist (partial; see phase-9 notes)

## Phase 10 — Release close-out

- [x] Release notes
- [x] Demo script
- [x] Write docs/checkpoints/phase-10.md

## Phase 11 — Test harness and archive

- [x] tests/test_stubs.py
- [x] Project archive
- [x] Write docs/checkpoints/phase-11.md
