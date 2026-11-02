import { useState, useMemo } from "react";

const CHAPTERS = [
  { id: "getting-started", title: "Getting Started", file: "01-getting-started.md" },
  { id: "chatting", title: "Chatting with the Agent", file: "02-chatting.md" },
  { id: "files", title: "Finding Your Files", file: "03-files.md" },
  { id: "email", title: "Connecting Email", file: "04-email.md" },
  { id: "mls", title: "Working with MLS Data", file: "05-mls.md" },
  { id: "verification", title: "Verification Explained", file: "06-verification.md" },
  { id: "bots", title: "Bots and Workflows", file: "07-bots.md" },
  { id: "charts", title: "Charts and Reports", file: "08-charts.md" },
  { id: "models", title: "Models and Hardware", file: "09-models.md" },
  { id: "connectors", title: "Connectors and MCP", file: "10-connectors.md" },
  { id: "troubleshooting", title: "Troubleshooting", file: "11-troubleshooting.md" },
  { id: "privacy", title: "Privacy and Safety", file: "12-privacy.md" },
];

// Inline content so the overlay works without a fetch layer in this phase.
const CONTENT: Record<string, string> = {
  "getting-started": "Your computer was scanned on first launch. The app recommended a model that fits your hardware and downloaded it.\n\nThree buttons appear after setup:\n- Search my files — indexes folders you choose\n- Connect my email — links Gmail or Outlook\n- Start chatting — opens the chat view\n\nEvery response is checked against your source data before you can copy or send it.",
  chatting: "Type a question or use a quick action above the input. Tool calls appear as chips inside the response. The verification table below the draft lists every claim as supported or unsupported. Copy and Send stay disabled while any unsupported claim remains. Use the Fix button to correct or remove it.\n\nType / to see commands.",
  files: "Click Add folder in the Files view. Supported formats include PDF, CSV, and plain text. Scanned documents are processed so their text becomes searchable. Only the folders you add are indexed. Client financial details should stay out of public tools.",
  email: "In Settings → Connectors choose Email. Sign in with Gmail or Outlook, or enter IMAP details. Message bodies stay on this machine when you use the local model. Switching to a cloud model shows a confirmation warning.",
  mls: "Export a CSV from your MLS and upload it in the MLS/CSV view. You can ask the agent to sort by square footage or flag price outliers. The agent drafts narratives from the rows you provide; it does not set a value.",
  verification: "A claim is a single factual statement in a draft. Supported means the fact appears in your source data. Unsupported means it does not. The slider sets how many verification passes run (1 = Fast, 2 = Standard, 3 = Strict). Copy and Send remain disabled until every unsupported claim is fixed.",
  bots: "A bot is a saved agent with a name, a subset of tools, and a system prompt. You can schedule it. Write actions (send email, modify a file) always show a preview and require confirmation.",
  charts: "Ask for a chart in chat or open the Charts view. Choose bar, line, or scatter. Export the image as PNG. Charts are generated from the data you have already indexed.",
  models: "The app chooses a model that fits your RAM and CPU. On an 8 GB laptop it recommends a small model. You can switch models from the top bar or with /model. Larger models write better prose but still require verification.",
  connectors: "Settings → Connectors lists curated servers (Filesystem, Email, Calendar, MLS). The Share this harness toggle exposes the app as an MCP server over SSE. The local API is bound to 127.0.0.1 and requires a token. Network exposure requires an explicit warning.",
  troubleshooting: "1. If the model fails to load, type /status and check the memory line.\n2. If available memory is low, close other applications or switch to a smaller model with /model.\n3. Type /logs to open the Activity Log and look for the latest error.\n4. If email will not sync, open Settings → Connectors and toggle Email off then on.\n5. To reset the index, remove and re-add the folder in the Files view.\n6. Collect a debug bundle by enabling Debug in Settings and copying the JSON from the Debug tab.",
  privacy: "The default model runs on this device. Client data does not leave the machine unless you explicitly switch to a cloud model and confirm the warning. The listing writer blocks high-risk fair-housing phrases. Every write action requires a preview. Retrieved content is treated as data, never as instructions.",
};

interface ManualOverlayProps {
  open: boolean;
  onClose: () => void;
  initialChapter?: string;
}

export function ManualOverlay({ open, onClose, initialChapter = "getting-started" }: ManualOverlayProps) {
  const [chapter, setChapter] = useState(initialChapter);
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    if (!query.trim()) return CHAPTERS;
    const q = query.toLowerCase();
    return CHAPTERS.filter(
      (c) => c.title.toLowerCase().includes(q) || (CONTENT[c.id] || "").toLowerCase().includes(q)
    );
  }, [query]);

  if (!open) return null;

  const body = CONTENT[chapter] || "Chapter not found.";

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "#11111b",
        zIndex: 100,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", padding: "12px 16px", borderBottom: "1px solid #313244" }}>
        <strong>Help</strong>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search the manual…"
          style={{ marginLeft: 16, flex: 1, maxWidth: 300, background: "#1e1e2e", color: "#cdd6f4", border: "1px solid #45475a", borderRadius: 4, padding: "4px 8px" }}
        />
        <button onClick={onClose} style={{ marginLeft: "auto", background: "none", border: "none", color: "#cdd6f4", cursor: "pointer", fontSize: 18 }}>
          ✕
        </button>
      </div>
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <nav style={{ width: 220, borderRight: "1px solid #313244", overflow: "auto", padding: 8 }}>
          {filtered.map((c) => (
            <button
              key={c.id}
              onClick={() => setChapter(c.id)}
              style={{
                display: "block",
                width: "100%",
                textAlign: "left",
                padding: "6px 8px",
                background: chapter === c.id ? "#313244" : "transparent",
                border: "none",
                color: "#cdd6f4",
                cursor: "pointer",
                fontSize: 13,
              }}
            >
              {c.title}
            </button>
          ))}
        </nav>
        <div style={{ flex: 1, overflow: "auto", padding: 24, whiteSpace: "pre-wrap", lineHeight: 1.6 }}>
          {body}
          <div style={{ marginTop: 32, fontSize: 13, color: "#a6adc8" }}>
            Was this helpful?{" "}
            <button style={{ fontSize: 12 }}>Yes</button>{" "}
            <button style={{ fontSize: 12 }}>No</button>
          </div>
        </div>
      </div>
    </div>
  );
}
