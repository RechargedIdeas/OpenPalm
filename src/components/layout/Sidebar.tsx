import { useUI, View } from "../../stores/ui";

const items: { id: View; label: string; icon: string }[] = [
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "files", label: "Files", icon: "📁" },
  { id: "email", label: "Email", icon: "✉️" },
  { id: "mls", label: "MLS/CSV", icon: "📊" },
  { id: "charts", label: "Charts", icon: "📈" },
  { id: "models", label: "Models", icon: "🧠" },
  { id: "watchdog", label: "Watchdog", icon: "🛡️" },
  { id: "training", label: "Training", icon: "🧪" },
  { id: "system", label: "System", icon: "🔧" },
  { id: "activity", label: "Activity", icon: "📋" },
  { id: "settings", label: "Settings", icon: "⚙️" },
];

export function Sidebar() {
  const { activeView, setActiveView, sidebarCollapsed } = useUI();

  return (
    <aside
      style={{
        width: sidebarCollapsed ? 60 : 220,
        background: "var(--surface)",
        color: "var(--text)",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.2s",
        borderRight: "1px solid var(--border)",
      }}
    >
      <div style={{ padding: "16px 12px", fontWeight: 600, fontSize: 14 }}>
        {sidebarCollapsed ? "OP" : "OpenPalm"}
      </div>
      <nav style={{ flex: 1 }}>
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 12,
              width: "100%",
              padding: "10px 12px",
              background: activeView === item.id ? "var(--border)" : "transparent",
              color: activeView === item.id ? "var(--accent)" : "var(--text)",
              border: "none",
              cursor: "pointer",
              textAlign: "left",
              fontSize: 14,
            }}
          >
            <span>{item.icon}</span>
            {!sidebarCollapsed && <span>{item.label}</span>}
          </button>
        ))}
      </nav>
    </aside>
  );
}
