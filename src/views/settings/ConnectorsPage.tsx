import { useState } from "react";

interface Connector {
  id: string;
  name: string;
  description: string;
  connected: boolean;
}

const INITIAL: Connector[] = [
  { id: "filesystem", name: "Filesystem", description: "Search local folders and files", connected: false },
  { id: "email", name: "Email", description: "Gmail, Outlook, or IMAP", connected: false },
  { id: "calendar", name: "Google Calendar", description: "Read and create events", connected: false },
  { id: "mls", name: "MLS / CSV", description: "Query listing exports", connected: false },
];

export function ConnectorsPage() {
  const [connectors, setConnectors] = useState(INITIAL);
  const [shareEnabled, setShareEnabled] = useState(false);
  const [apiToken, setApiToken] = useState("••••••••••••••••");
  const [showToken, setShowToken] = useState(false);
  const [networkWarned, setNetworkWarned] = useState(false);

  const toggle = (id: string) => {
    setConnectors((cs) => cs.map((c) => (c.id === id ? { ...c, connected: !c.connected } : c)));
  };

  const regenerate = () => {
    setApiToken("tok_" + Math.random().toString(36).slice(2, 10));
    setShowToken(true);
  };

  return (
    <div style={{ padding: 24, maxWidth: 720 }}>
      <h2 style={{ marginTop: 0 }}>Connectors</h2>
      <p style={{ color: "#a6adc8", marginBottom: 16 }}>
        Connect external tools. Each card is a curated MCP server.
      </p>
      <div style={{ display: "grid", gap: 12 }}>
        {connectors.map((c) => (
          <div
            key={c.id}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              padding: 12,
              background: "#1e1e2e",
              border: "1px solid #313244",
              borderRadius: 6,
            }}
          >
            <span
              style={{
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: c.connected ? "#a6e3a1" : "#585b70",
              }}
            />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600 }}>{c.name}</div>
              <div style={{ fontSize: 13, color: "#a6adc8" }}>{c.description}</div>
            </div>
            <button
              onClick={() => toggle(c.id)}
              style={{
                padding: "4px 12px",
                background: c.connected ? "#313244" : "#89b4fa",
                color: c.connected ? "#cdd6f4" : "#11111b",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              {c.connected ? "Disconnect" : "Connect"}
            </button>
          </div>
        ))}
      </div>

      <h2 style={{ marginTop: 32 }}>Share this harness</h2>
      <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <input
          type="checkbox"
          checked={shareEnabled}
          onChange={(e) => setShareEnabled(e.target.checked)}
        />
        Expose MCP server (SSE)
      </label>
      {shareEnabled && (
        <div style={{ fontSize: 13, color: "#a6adc8", marginBottom: 8 }}>
          Endpoint: <code>http://127.0.0.1:0/sse</code>{" "}
          <button
            onClick={() => navigator.clipboard?.writeText("http://127.0.0.1:0/sse")}
            style={{ fontSize: 12, marginLeft: 8 }}
          >
            Copy
          </button>
        </div>
      )}

      <h2 style={{ marginTop: 32 }}>Local API</h2>
      <p style={{ fontSize: 13, color: "#a6adc8" }}>
        Bound to 127.0.0.1. Network exposure requires confirmation.
      </p>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <code style={{ background: "#1e1e2e", padding: "4px 8px", borderRadius: 4 }}>
          {showToken ? apiToken : "••••••••••••••••"}
        </code>
        <button onClick={() => setShowToken((s) => !s)} style={{ fontSize: 12 }}>
          {showToken ? "Hide" : "Show"}
        </button>
        <button onClick={regenerate} style={{ fontSize: 12 }}>
          Regenerate
        </button>
      </div>
      <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12 }}>
        <input
          type="checkbox"
          checked={networkWarned}
          onChange={(e) => {
            if (e.target.checked) {
              if (window.confirm("Exposing the API on the network can leak client data. Continue?")) {
                setNetworkWarned(true);
              }
            } else {
              setNetworkWarned(false);
            }
          }}
        />
        Allow network access (warned opt-in)
      </label>
    </div>
  );
}
