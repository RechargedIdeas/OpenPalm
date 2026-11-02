import { useState, useEffect } from "react";
import { useUI } from "../stores/ui";
import { ConnectorsPage } from "./settings/ConnectorsPage";
import { BotWizard } from "./BotWizard";

type Section = "general" | "model" | "connectors" | "bots" | "help";

const SIDECAR = "http://127.0.0.1:8765";

export function SettingsView() {
  const { theme, toggleTheme, setManualOpen } = useUI();
  const [section, setSection] = useState<Section>("general");
  const [model, setModel] = useState("phi4-mini");
  const [verifyPasses, setVerifyPasses] = useState(2);
  const [strictMode, setStrictMode] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${SIDECAR}/data`);
        if (r.ok) {
          const d = await r.json();
          if (d.settings?.model) setModel(d.settings.model);
          if (d.settings?.passes) setVerifyPasses(d.settings.passes);
          if (typeof d.settings?.strict === "boolean") setStrictMode(d.settings.strict);
        }
      } catch {}
    })();
  }, []);

  const save = async (next: { model?: string; passes?: number; strict?: boolean }) => {
    const body = { model, passes: verifyPasses, strict: strictMode, ...next };
    try {
      await fetch(`${SIDECAR}/data/settings`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 1200);
    } catch {}
  };

  const sections: { id: Section; label: string }[] = [
    { id: "general", label: "General" },
    { id: "model", label: "Model" },
    { id: "connectors", label: "Connectors" },
    { id: "bots", label: "Bots" },
    { id: "help", label: "Help" },
  ];

  return (
    <div style={{ display: "flex", height: "100%", background: "var(--bg)", color: "var(--text)" }}>
      <nav
        style={{
          width: 180,
          borderRight: "1px solid var(--border)",
          padding: "16px 0",
          background: "var(--surface)",
        }}
      >
        {sections.map((s) => (
          <button
            key={s.id}
            onClick={() => setSection(s.id)}
            style={{
              display: "block",
              width: "100%",
              textAlign: "left",
              padding: "10px 16px",
              background: section === s.id ? "var(--border)" : "transparent",
              color: "var(--text)",
              border: "none",
              cursor: "pointer",
              fontSize: 14,
            }}
          >
            {s.label}
          </button>
        ))}
      </nav>

      <div style={{ flex: 1, overflow: "auto", padding: 24 }}>
        {saved && <div style={{ fontSize: 12, color: "var(--ok)", marginBottom: 12 }}>Saved</div>}

        {section === "general" && (
          <div style={{ maxWidth: 560 }}>
            <h2 style={{ marginTop: 0 }}>General</h2>

            <div style={{ marginBottom: 24 }}>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>Appearance</div>
              <label style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span>Theme</span>
                <button
                  onClick={toggleTheme}
                  style={{
                    padding: "6px 14px",
                    background: "var(--surface)",
                    border: "1px solid var(--border)",
                    color: "var(--text)",
                    borderRadius: 4,
                    cursor: "pointer",
                  }}
                >
                  {theme === "dark" ? "☀️ Light mode" : "🌙 Dark mode"}
                </button>
              </label>
              <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>
                Current: {theme}. Saved automatically.
              </p>
            </div>

            <div style={{ marginBottom: 24 }}>
              <div style={{ fontWeight: 600, marginBottom: 8 }}>Verification</div>
              <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <input
                  type="checkbox"
                  checked={strictMode}
                  onChange={(e) => {
                    setStrictMode(e.target.checked);
                    save({ strict: e.target.checked });
                  }}
                />
                Strict mode (block Copy while unsupported claims remain)
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span>Verification passes</span>
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={verifyPasses}
                  onChange={(e) => {
                    const n = Number(e.target.value);
                    setVerifyPasses(n);
                    save({ passes: n });
                  }}
                  style={{
                    width: 60,
                    padding: 4,
                    background: "var(--surface)",
                    color: "var(--text)",
                    border: "1px solid var(--border)",
                    borderRadius: 4,
                  }}
                />
              </label>
              <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>
                How many times OpenPalm checks claims against your sources.
              </p>
            </div>
          </div>
        )}

        {section === "model" && (
          <div style={{ maxWidth: 560 }}>
            <h2 style={{ marginTop: 0 }}>Model</h2>
            <label style={{ display: "block", marginBottom: 16 }}>
              <div style={{ marginBottom: 6 }}>Local model</div>
              <select
                value={model}
                onChange={(e) => {
                  setModel(e.target.value);
                  save({ model: e.target.value });
                }}
                style={{
                  padding: "6px 10px",
                  background: "var(--surface)",
                  color: "var(--text)",
                  border: "1px solid var(--border)",
                  borderRadius: 4,
                  minWidth: 200,
                }}
              >
                <option value="phi4-mini">Phi-4-mini</option>
                <option value="qwen3-1.7b">Qwen3 1.7B</option>
                <option value="llama3.2-1b">Llama 3.2 1B</option>
              </select>
            </label>
            <p style={{ fontSize: 13, color: "var(--muted)" }}>
              Runs on CPU by default. No GPU required. Change takes effect on the next message.
            </p>
          </div>
        )}

        {section === "connectors" && <ConnectorsPage />}
        {section === "bots" && <BotWizard />}

        {section === "help" && (
          <div style={{ maxWidth: 560 }}>
            <h2 style={{ marginTop: 0 }}>Help</h2>
            <p style={{ color: "var(--muted)", marginBottom: 16 }}>
              Open the full user manual or jump to a section.
            </p>
            <button
              onClick={() => setManualOpen(true)}
              style={{ padding: "8px 16px", background: "var(--accent)", color: "#11111b", border: "none", borderRadius: 4, cursor: "pointer" }}
            >
              Open manual
            </button>
            <ul style={{ marginTop: 16, fontSize: 14, lineHeight: 1.8 }}>
              <li>Paste sources above the chat input so claims can be checked.</li>
              <li>Copy stays off until every claim is supported (in strict mode).</li>
              <li>Server controls are in the top bar: Start, Stop, Reset.</li>
              <li>Both GUIs share chat, settings, and sources.</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
