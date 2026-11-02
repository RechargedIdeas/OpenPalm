import { useUI } from "../../stores/ui";
import { ServerControl } from "../server/ServerControl";

export function TopBar() {
  const { toggleSidebar, bottomCollapsed, setBottomCollapsed, setManualOpen, theme, toggleTheme } = useUI();

  return (
    <header
      style={{
        height: 48,
        background: "var(--surface-2)",
        borderBottom: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        padding: "0 12px",
        gap: 12,
        color: "var(--text)",
      }}
    >
      <button
        onClick={toggleSidebar}
        style={{ background: "none", border: "none", color: "var(--text)", cursor: "pointer", fontSize: 18 }}
        aria-label="Toggle sidebar"
      >
        ≡
      </button>
      <strong style={{ fontSize: 15 }}>OpenPalm</strong>
      <ServerControl />
      <select
        defaultValue="phi4-mini"
        style={{ marginLeft: "auto", background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: "4px 8px" }}
      >
        <option value="phi4-mini">Phi-4-mini</option>
        <option value="qwen3-1.7b">Qwen3 1.7B</option>
      </select>
      <button
        onClick={toggleTheme}
        style={{ background: "none", border: "none", color: "var(--text)", cursor: "pointer", fontSize: 16 }}
        aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
        title={theme === "dark" ? "Light mode" : "Dark mode"}
      >
        {theme === "dark" ? "☀️" : "🌙"}
      </button>
      <button style={{ background: "none", border: "none", color: "var(--text)", cursor: "pointer" }}>🔍</button>
      <button style={{ background: "none", border: "none", color: "var(--text)", cursor: "pointer" }}>⚙</button>
      <button onClick={() => setManualOpen(true)} style={{ background: "none", border: "none", color: "var(--text)", cursor: "pointer" }}>Help</button>
      {bottomCollapsed && (
        <button
          onClick={() => setBottomCollapsed(false)}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", color: "var(--text)", padding: "4px 8px", borderRadius: 4, cursor: "pointer", fontSize: 12 }}
        >
          Terminal
        </button>
      )}
    </header>
  );
}
