import { useState } from "react";

export function BotWizard() {
  const [name, setName] = useState("Seller follow-up");
  const [prompt, setPrompt] = useState("Draft a friendly check-in. Never commit to a price.");
  const [tools, setTools] = useState(["email", "calendar"]);
  const [created, setCreated] = useState(false);

  const toggleTool = (t: string) => {
    setTools((ts) => (ts.includes(t) ? ts.filter((x) => x !== t) : [...ts, t]));
  };

  return (
    <div style={{ padding: 24, maxWidth: 480 }}>
      <h2 style={{ marginTop: 0 }}>Create a bot</h2>
      <label style={{ display: "block", marginBottom: 8 }}>
        Name
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          style={{ display: "block", width: "100%", marginTop: 4, padding: 6, background: "#1e1e2e", color: "#cdd6f4", border: "1px solid #45475a", borderRadius: 4 }}
        />
      </label>
      <label style={{ display: "block", marginBottom: 8 }}>
        System prompt
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={3}
          style={{ display: "block", width: "100%", marginTop: 4, padding: 6, background: "#1e1e2e", color: "#cdd6f4", border: "1px solid #45475a", borderRadius: 4 }}
        />
      </label>
      <div style={{ marginBottom: 12 }}>
        Tools: {["email", "calendar", "mls", "files"].map((t) => (
          <label key={t} style={{ marginRight: 12 }}>
            <input type="checkbox" checked={tools.includes(t)} onChange={() => toggleTool(t)} /> {t}
          </label>
        ))}
      </div>
      <button
        onClick={() => setCreated(true)}
        style={{ padding: "8px 16px", background: "#89b4fa", color: "#11111b", border: "none", borderRadius: 4, cursor: "pointer" }}
      >
        Create bot
      </button>
      {created && (
        <div style={{ marginTop: 16, color: "#a6e3a1" }}>
          Bot “{name}” created. It will draft emails using: {tools.join(", ")}.
        </div>
      )}
    </div>
  );
}
