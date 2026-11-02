import { useState, useEffect } from "react";

const BASE = "http://127.0.0.1:8765";

export function WatchdogView() {
  const [status, setStatus] = useState<any>(null);
  const [scanText, setScanText] = useState("");
  const [result, setResult] = useState("");

  const load = async () => {
    try {
      const r = await fetch(`${BASE}/watchdog`);
      setStatus(await r.json());
    } catch {}
  };

  useEffect(() => { load(); const t = setInterval(load, 3000); return () => clearInterval(t); }, []);

  const scan = async () => {
    const r = await fetch(`${BASE}/watchdog/scan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: scanText, source: "dashboard" }) });
    const d = await r.json();
    setResult(d.ok ? "clean" : `blocked: ${d.alerts.map((a: any) => a.kind).join(", ")}`);
    load();
  };

  const cleanup = async (source: string) => {
    await fetch(`${BASE}/watchdog/cleanup`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ source }) });
    load();
  };

  const runSecurity = async (name: string) => {
    const r = await fetch(`${BASE}/security/${name}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: scanText || "status" }) });
    const d = await r.json();
    setResult(JSON.stringify(d).slice(0, 150));
    load();
  };

  return (
    <div style={{ padding: 24, color: "var(--text)" }}>
      <h2 style={{ marginTop: 0 }}>Watchdog</h2>
      <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 12 }}>
        {status ? `${status.alerts} alerts · ${status.blocked?.length || 0} blocked · ${status.enabled ? "on" : "off"}` : "loading…"}
      </div>

      <section style={{ marginBottom: 16 }}>
        <h3>Scan</h3>
        <textarea value={scanText} onChange={(e) => setScanText(e.target.value)} placeholder="Paste code or output to scan" style={{ width: "100%", height: 60, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 8 }} />
        <button onClick={scan} style={{ marginTop: 4, fontSize: 12 }}>Scan</button>
        {result && <div style={{ fontSize: 13, marginTop: 4 }}>{result}</div>}
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>Security models</h3>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {["guard", "policy", "auditor", "isolator", "cleaner"].map(s => (
            <button key={s} onClick={() => runSecurity(s)} style={{ fontSize: 12 }}>{s}</button>
          ))}
        </div>
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>Blocked</h3>
        {(status?.blocked || []).length === 0 && <div style={{ fontSize: 13, color: "var(--muted)" }}>None</div>}
        {(status?.blocked || []).map((s: string) => (
          <div key={s} style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 4 }}>
            <code>{s}</code>
            <button onClick={() => cleanup(s)} style={{ fontSize: 11 }}>Cleanup</button>
          </div>
        ))}
      </section>

      
      <section style={{ marginTop: 16 }}>
        <h3>Training</h3>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          <button onClick={async () => { await fetch(`${BASE}/watchdog/train/manual`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: scanText || "os.system", kind: "manual" }) }); load(); }} style={{ fontSize: 12 }}>Train manual</button>
          <button onClick={async () => { const r = await fetch(`${BASE}/watchdog/train/from-rama`, { method: "POST" }); const d = await r.json(); setResult(`taught ${d.taught || 0} from RAMA`); load(); }} style={{ fontSize: 12 }}>Train from RAMA</button>
          <button onClick={async () => { await fetch(`${BASE}/watchdog/train/rollback`, { method: "POST" }); load(); }} style={{ fontSize: 12 }}>Rollback</button>
        </div>
        <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>Live · polls every 3s · SSE at /watchdog/stream</div>
      </section>

      <section>
        <h3>Recent alerts</h3>
        <div style={{ fontSize: 12, background: "#111", padding: 8, borderRadius: 4, maxHeight: 200, overflow: "auto" }}>
          {(status?.recent || []).map((a: any, i: number) => (
            <div key={i} style={{ color: a.kind === "escape" || a.kind === "harmful" ? "var(--bad)" : "var(--muted)" }}>
              [{a.kind}] {a.source}: {a.detail} {a.action && `(${a.action})`}
            </div>
          ))}
          {!(status?.recent || []).length && <div style={{ color: "var(--muted)" }}>No alerts</div>}
        </div>
      </section>
    </div>
  );
}
