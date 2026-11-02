import { useState, useEffect } from "react";

const BASE = "http://127.0.0.1:8765";

export function ModelsView() {
  const [data, setData] = useState<any>(null);
  const [filter, setFilter] = useState("");

  const load = async () => {
    try {
      const r = await fetch(`${BASE}/catalog${filter ? `?type=${filter}` : ""}`);
      setData(await r.json());
    } catch {}
  };

  useEffect(() => { load(); }, [filter]);

  const models = data?.models || [];
  const hw = data?.hardware;

  return (
    <div style={{ padding: 24, color: "var(--text)" }}>
      <h2 style={{ marginTop: 0 }}>Model Management</h2>
      {hw && <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 12 }}>RAM {hw.ram_gb} GB · VRAM {hw.vram_gb} GB · {hw.backend} · GPU {hw.gpu ? "yes" : "no"}</div>}
      <div style={{ display: "flex", gap: 4, marginBottom: 12, flexWrap: "wrap" }}>
        <button onClick={() => setFilter("")} style={{ fontSize: 12, padding: "4px 10px", background: !filter ? "var(--border)" : "transparent", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4 }}>all</button>
        {(data?.types || []).map((t: string) => (
          <button key={t} onClick={() => setFilter(t)} style={{ fontSize: 12, padding: "4px 10px", background: filter === t ? "var(--border)" : "transparent", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4 }}>{t}</button>
        ))}
      </div>
      <div style={{ display: "grid", gap: 8 }}>
        {models.map((m: any) => (
          <div key={m.id} style={{ background: "var(--surface)", padding: 12, borderRadius: 6, display: "flex", gap: 12, alignItems: "center" }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 600 }}>{m.name} <span style={{ fontSize: 11, color: "var(--muted)" }}>{m.type} · {m.params}</span></div>
              <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 2 }}>{m.uses.join(" · ")}</div>
            </div>
            <div style={{ textAlign: "right", fontSize: 12 }}>
              <div style={{ color: m.fit === "gpu" ? "var(--ok)" : m.fit === "cpu" ? "var(--warn, #f9e2af)" : "var(--bad)" }}>{m.fit}</div>
              <div>{m.est_tps > 0 ? `~${m.est_tps} tok/s` : "—"}</div>
              <div style={{ color: "var(--muted)" }}>{m.vram_gb} GB</div>
              {m.hf && <button onClick={async () => { const r = await fetch(`${BASE}/hf/download`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ repo: m.hf }) }); const d = await r.json(); alert(d.ok ? "Downloaded" : d.error); }} style={{ fontSize: 10, marginTop: 4 }}>Download</button>}
            </div>
          </div>
        ))}
      
      <section style={{ marginTop: 24 }}>
        <h3>Watchdog</h3>
        <div style={{ display: "flex", gap: 6, marginBottom: 8 }}>
          {["guard", "policy", "auditor", "isolator", "cleaner"].map(s => (
            <button key={s} onClick={async () => {
              const r = await fetch(`${BASE}/security/${s}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: "os.system('id')" }) });
              const d = await r.json();
              alert(JSON.stringify(d).slice(0, 120));
            }} style={{ fontSize: 11 }}>{s}</button>
          ))}
          <button onClick={async () => { await fetch(`${BASE}/watchdog/cleanup`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ source: "model" }) }); }} style={{ fontSize: 11 }}>Cleanup</button>
        </div>
      </section>

    </div>
  );
}
