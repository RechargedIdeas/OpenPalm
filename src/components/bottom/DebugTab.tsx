export function DebugTab() {
  const sample = {
    tool: "search_files",
    args: { query: "123 Main St", limit: 5 },
    duration_ms: 142,
    tokens: 87,
  };

  return (
    <div style={{ height: "100%", overflow: "auto", padding: 8, fontFamily: "ui-monospace, monospace", fontSize: 12, color: "#cdd6f4" }}>
      <pre style={{ margin: 0 }}>{JSON.stringify(sample, null, 2)}</pre>
      <div style={{ marginTop: 12, color: "#585b70", fontStyle: "italic" }}>
        (stub) — raw JSON-RPC and tool payloads appear here when Debug is enabled in Settings
      </div>
    </div>
  );
}
