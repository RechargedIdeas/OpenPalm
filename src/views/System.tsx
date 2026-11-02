import { useState, useEffect } from "react";
import { api } from "../api/client";

export function SystemView() {
  const [health, setHealth] = useState<any>(null);
  const [pair, setPair] = useState<any>(null);
  const [snaps, setSnaps] = useState<string[]>([]);
  const [backends, setBackends] = useState<any>(null);
  const [unified, setUnified] = useState<any>(null);
  const [status, setStatus] = useState("");
  const [sandbox, setSandbox] = useState<any>(null);
  const [ramaOut, setRamaOut] = useState("");
  const [prompt, setPrompt] = useState("");

  const refresh = async () => {
    try {
      const [h, p, s, b, u] = await Promise.all([
        api.health().catch(() => null),
        api.pairStatus().catch(() => null),
        api.snapshots().catch(() => ({ snapshots: [] })),
        api.backends().catch(() => null),
        api.unifiedStats().catch(() => null),
        fetch("http://127.0.0.1:8765/sandbox").then(r => r.json()).catch(() => null),
      ]);
      setHealth(h); setPair(p); setSnaps(s.snapshots || []); setBackends(b); setUnified(u); setSandbox(arguments[0] && null);
    } catch { setStatus("Server unreachable"); }
  };

  useEffect(() => { refresh(); const t = setInterval(refresh, 4000); return () => clearInterval(t); }, []);

  return (
    <div style={{ padding: 24, maxWidth: 720, color: "var(--text)" }}>
      <h2 style={{ marginTop: 0 }}>System</h2>
      {status && <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 8 }}>{status}</div>}

      
      <section style={{ marginBottom: 16 }}>
        <h3>Sandbox</h3>
        <label style={{ fontSize: 14 }}>
          <input type="checkbox" checked={sandbox?.isolate !== false} onChange={async (e) => {
            const r = await fetch("http://127.0.0.1:8765/sandbox/toggle", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ isolate: e.target.checked }) });
            setSandbox(await r.json());
          }} /> Isolate processes (default on)
        </label>
        <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4 }}>{sandbox ? `Backend: ${sandbox.backend} · available: ${sandbox.backend_available}` : "loading…"}</div>
        <button onClick={async () => {
          const r = await fetch("http://127.0.0.1:8765/sandbox");
          setSandbox(await r.json());
        }} style={{ fontSize: 11, marginTop: 4 }}>Refresh</button>
      </section>

      
      <section style={{ marginBottom: 16 }}>
        <h3>Terminal <button id="termCopy" onClick={() => { const t = document.getElementById("termOut")?.textContent || ""; navigator.clipboard.writeText(t); }} style={{ fontSize: 11, marginLeft: 8 }}>Copy</button>
        <button onClick={() => { const t = document.getElementById("termOut")?.textContent || ""; const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([t])); a.download = "terminal.txt"; a.click(); }} style={{ fontSize: 11 }}>Export</button> <span style={{ fontSize: 10, color: "var(--muted)" }}>Ctrl+Shift+C copy · Ctrl+S export</span></h3>
        <div style={{ display: "flex", gap: 8, marginBottom: 4 }}>
          <label style={{ fontSize: 12 }}><input type="checkbox" onChange={async (e) => { await fetch("http://127.0.0.1:8765/sandbox/network", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ enabled: e.target.checked }) }); }} /> Network</label>
          <label style={{ fontSize: 12 }}><input type="checkbox" onChange={async (e) => { await fetch("http://127.0.0.1:8765/sandbox/gpu", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ enabled: e.target.checked }) }); }} /> GPU</label>
        </div>
        <input id="termCmd" placeholder="command" style={{ width: "70%", background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 6 }} onKeyDown={async (e) => {
          if (e.key === "Enter") {
            const cmd = (e.target as HTMLInputElement).value;
            const r = await fetch("http://127.0.0.1:8765/terminal/cmd", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ line: cmd }) });
            const d = await r.json();
            const out = document.getElementById("termOut");
            if (out) out.textContent = (d.stdout || d.error || "") + (d.stderr || "");
          }
        }} />
        <pre id="termOut" style={{ fontSize: 12, background: "#111", color: "#0f0", padding: 8, borderRadius: 4, minHeight: 60, marginTop: 4 }} />
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>Health</h3>
        <pre style={{ fontSize: 12, background: "var(--surface)", padding: 8, borderRadius: 4 }}>{JSON.stringify(health, null, 2)}</pre>
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>Pairing</h3>
        <div style={{ fontSize: 13 }}>{pair ? `Status: ${JSON.stringify(pair)}` : "—"}</div>
        <button onClick={async () => { const c = await api.pairCode(); setStatus(`Code: ${c.code}`); }} style={{ marginTop: 4, fontSize: 12 }}>Generate code</button>
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>RAMA</h3>
        <input value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="Prompt" style={{ width: "60%", marginRight: 8, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 6 }} />
        <button onClick={async () => { const r = await api.rama(prompt || "hello"); setRamaOut(r.output || JSON.stringify(r)); }} style={{ fontSize: 12 }}>Run</button>
        {ramaOut && <pre style={{ fontSize: 12, background: "var(--surface)", padding: 8, borderRadius: 4, marginTop: 4 }}>{ramaOut.slice(0, 200)}</pre>}
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>Snapshots</h3>
        <button onClick={async () => { await api.snapshot({ note: "ui" }, "manual"); refresh(); }} style={{ fontSize: 12 }}>Take snapshot</button>
        <ul style={{ fontSize: 12, listStyle: "none", padding: 0 }}>
          {snaps.map((s) => <li key={s}><code>{s}</code></li>)}
        </ul>
      </section>

      <section style={{ marginBottom: 16 }}>
        <h3>Backends</h3>
        <pre style={{ fontSize: 12, background: "var(--surface)", padding: 8, borderRadius: 4 }}>{JSON.stringify(backends, null, 2)}</pre>
      </section>

      <section>
        <h3>Unified memory</h3>
        <div style={{ fontSize: 13 }}>{unified ? JSON.stringify(unified) : "—"}</div>
        <button onClick={async () => { await api.unifiedAlloc("ui-buf", 1024); refresh(); }} style={{ marginTop: 4, fontSize: 12 }}>Alloc 1KB</button>
      </section>
    </div>
  );
}
