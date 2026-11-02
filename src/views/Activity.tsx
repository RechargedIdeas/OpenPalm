import { useState, useEffect } from "react";

const BASE = "http://127.0.0.1:8765";

export function ActivityView() {
  const [entries, setEntries] = useState<any[]>([]);
  const [filter, setFilter] = useState("");

  const load = async () => {
    try {
      const r = await fetch(`${BASE}/activity`);
      const d = await r.json();
      setEntries(d.entries || []);
    } catch {}
  };

  useEffect(() => { load(); const t = setInterval(load, 2000); return () => clearInterval(t); }, []);
  useEffect(() => {
    const es = new EventSource(`${BASE}/monitor/stream`);
    es.onmessage = (e) => {
      const el = document.getElementById("liveMon");
      if (el) {
        const d = JSON.parse(e.data);
        const jobs = (d.training?.active || []).length;
        const alerts = d.watchdog?.alerts || 0;
        const logs = (d.logs || []).slice(-3).map((l: any) => `[${l.level}] ${l.message}`).join("\n");
        el.textContent = `jobs: ${jobs} · alerts: ${alerts}\n${logs || "no recent logs"}`;
      }
    };
    return () => es.close();
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "c" && e.shiftKey) { e.preventDefault(); copy(); }
      if ((e.metaKey || e.ctrlKey) && e.key === "s") { e.preventDefault(); save(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [text]);

  const text = entries.filter(e => !filter || e.level === filter).map(e => `[${e.level}] ${e.message}`).join("\n");

  const copy = () => navigator.clipboard.writeText(text);
  const save = () => {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([text], { type: "text/plain" }));
    a.download = "activity.log";
    a.click();
  };

  return (
    <div style={{ padding: 24, color: "var(--text)" }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <h2 style={{ margin: 0 }}>Activity</h2>
        <button onClick={copy} style={{ marginLeft: "auto", fontSize: 12 }}>Copy</button>
        <button onClick={save} style={{ fontSize: 12 }}>Export</button>
        <button onClick={async () => { await fetch(`${BASE}/activity/clear`, { method: "POST" }); load(); }} style={{ fontSize: 12 }}>Clear</button>
      </div>
      <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
        {["", "info", "debug", "error", "cmd"].map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{ fontSize: 11, padding: "2px 8px", background: filter === f ? "var(--border)" : "transparent", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4 }}>{f || "all"}</button>
        ))}
      </div>
      <pre style={{ fontSize: 12, background: "#111", color: "#ccc", padding: 8, borderRadius: 4, minHeight: 200, maxHeight: 400, overflow: "auto" }}>{text || "No activity yet."}</pre>
    
      <section style={{ marginTop: 16 }}>
        <h3>Live monitor</h3>
        <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 4 }}>SSE /monitor/stream · logs, training, watchdog, metrics</div>
        <pre id="liveMon" style={{ fontSize: 11, background: "#111", color: "#8f8", padding: 8, borderRadius: 4, maxHeight: 180, overflow: "auto" }}>connecting…</pre>
      </section>

    </div>
  );
}
