import { useState, useEffect, useRef } from "react";

const SIDECAR = "http://127.0.0.1:8765";

type Version = { id: string; label: string; ts: number };
type Job = { id: string; kind: string; target: string; status: string; progress: number; result?: any; error?: string };

export function TrainingView() {
  const [tab, setTab] = useState<"rama" | "ml">("rama");
  const [versions, setVersions] = useState<Version[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [telemetry, setTelemetry] = useState(false);
  const [samples, setSamples] = useState(0);
  const [prompt, setPrompt] = useState("");
  const [output, setOutput] = useState("");
  const [rating, setRating] = useState(3);
  const [note, setNote] = useState("");
  const [mlName, setMlName] = useState("");
  const [mlEpochs, setMlEpochs] = useState(1);
  const [status, setStatus] = useState("");
  const [hw, setHw] = useState<any>(null);
  const [models, setModels] = useState<any[]>([]);
  const [workers, setWorkers] = useState(1);
  const [batch, setBatch] = useState(1);
  const [metrics, setMetrics] = useState<any>(null);
  const poll = useRef<number | null>(null);

  const refresh = async () => {
    try {
      const [vr, sr, hr, mr] = await Promise.all([
        fetch(`${SIDECAR}/rama/versions`).then((r) => r.json()),
        fetch(`${SIDECAR}/train/status`).then((r) => r.json()),
        fetch(`${SIDECAR}/hardware`).then((r) => r.json()).catch(() => null),
        fetch(`${SIDECAR}/models/list`).then((r) => r.json()).catch(() => ({ models: [] })),
      ]);
      if (hr) { setHw(hr); setWorkers(hr.workers); setBatch(hr.batch_size); }
      setModels(mr.models || []);
      const met = await fetch(`${SIDECAR}/metrics`).then((r) => r.json()).catch(() => null);
      if (met) setMetrics(met);
      setVersions(vr.versions || []);
      setJobs(sr.jobs || []);
      setTelemetry(!!sr.telemetry);
      setSamples(sr.samples || 0);
    } catch {
      setStatus("Server unreachable");
    }
  };

  useEffect(() => {
    refresh();
    poll.current = window.setInterval(refresh, 2000);
    return () => { if (poll.current) clearInterval(poll.current); };
  }, []);

  const toggleTelemetry = async () => {
    const next = !telemetry;
    await fetch(`${SIDECAR}/train/telemetry`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: next }),
    });
    setTelemetry(next);
  };

  const submitFeedback = async () => {
    if (!prompt.trim()) return;
    setStatus("Sending…");
    await fetch(`${SIDECAR}/rama/feedback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, output, rating, note }),
    });
    setStatus("Feedback recorded");
    setPrompt(""); setOutput(""); setNote("");
    refresh();
  };

  const selfTrain = async () => {
    setStatus("Starting self-train…");
    const r = await fetch(`${SIDECAR}/train/self`, { method: "POST" });
    const d = await r.json();
    setStatus(`Job ${d.job} started`);
    refresh();
  };

  const manualTrain = async () => {
    if (!prompt.trim() || !note.trim()) return;
    setStatus("Starting manual…");
    await fetch(`${SIDECAR}/train/manual`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, specialist: note }),
    });
    setStatus("Manual job started");
    refresh();
  };

  const mlTrain = async () => {
    if (!mlName.trim()) return;
    setStatus("Starting ML train…");
    await fetch(`${SIDECAR}/train/ml`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: mlName, epochs: mlEpochs }),
    });
    setStatus("ML job started");
    refresh();
  };

  const rollback = async (id?: string) => {
    await fetch(`${SIDECAR}/rama/rollback`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    setStatus("Rolled back");
    refresh();
  };

  const active = jobs.filter((j) => j.status === "running" || j.status === "pending");

  return (
    <div style={{ padding: 24, maxWidth: 720, color: "var(--text)" }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button onClick={() => setTab("rama")} style={{ padding: "6px 14px", background: tab === "rama" ? "var(--border)" : "transparent", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, cursor: "pointer" }}>RAMA</button>
        <button onClick={() => setTab("ml")} style={{ padding: "6px 14px", background: tab === "ml" ? "var(--border)" : "transparent", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, cursor: "pointer" }}>ML Models</button>
        {active.length > 0 && <span style={{ marginLeft: "auto", fontSize: 12, color: "var(--ok)" }}>{active.length} job(s) running</span>}
        <button onClick={async () => {
          setStatus("Stopping…");
          const r = await fetch(`${SIDECAR}/train/stop`, { method: "POST" });
          const d = await r.json();
          setStatus(`Stopped ${d.count || 0} job(s)`);
          refresh();
        }} style={{ marginLeft: "auto", padding: "6px 12px", background: "var(--bad)", color: "#fff", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Stop all</button>
        <button onClick={async () => {
          setStatus("Stopping current…");
          const r = await fetch(`${SIDECAR}/train/stop/current`, { method: "POST" });
          const d = await r.json();
          setStatus(d.stopped ? `Stopped ${d.stopped}` : "Nothing running");
          refresh();
        }} style={{ padding: "6px 12px", background: "var(--warn, #f9e2af)", color: "#111", border: "none", borderRadius: 4, cursor: "pointer", fontSize: 12 }}>Stop current</button>


      </div>

      
      
      {metrics && (
        <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 8, display: "flex", gap: 12 }}>
          <span>CPU {metrics.cpu_percent}%</span>
          <span>RAM {metrics.ram_used_gb}/{metrics.ram_total_gb} GB ({metrics.ram_percent}%)</span>
          <span>{metrics.gpu_backend} {metrics.gpu_util}% VRAM {metrics.vram_used_mb}/{metrics.vram_total_mb} MB</span>
          <button onClick={async () => { await fetch(`${SIDECAR}/hardware/vram`, { method: "POST" }); setStatus("VRAM optimized"); }} style={{ fontSize: 11 }}>VRAM→RAM</button>
        </div>
      )}

      {hw && (
        <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 12, padding: "6px 8px", background: "var(--surface)", borderRadius: 4 }}>
          {hw.backend || hw.mode} · {hw.cpu_count} cores · {hw.gpu_count} GPU · {hw.memory_gb} GB · workers {hw.workers} · batch {hw.batch_size}{hw.unified_memory ? " · unified" : ""}
          <span style={{ marginLeft: 12 }}>
            <label>Workers <input type="number" min={1} max={64} value={workers} onChange={(e) => setWorkers(Number(e.target.value))} style={{ width: 50, marginLeft: 4 }} /></label>
            <label style={{ marginLeft: 8 }}>Batch <input type="number" min={1} max={32} value={batch} onChange={(e) => setBatch(Number(e.target.value))} style={{ width: 50, marginLeft: 4 }} /></label>
            <button onClick={async () => { await fetch(`${SIDECAR}/train/config`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ workers, batch_size: batch }) }); setStatus("Config saved"); }} style={{ marginLeft: 8, fontSize: 11 }}>Apply</button>
            <button onClick={async () => { setStatus("Benchmarking…"); const r = await fetch(`${SIDECAR}/hardware/bench`, { method: "POST" }); const d = await r.json(); setWorkers(d.recommended_workers); setBatch(d.recommended_batch); setStatus(`Bench: ${d.recommended_workers} workers, batch ${d.recommended_batch} (${d.duration_ms}ms)`); }} style={{ marginLeft: 8, fontSize: 11 }}>Auto-benchmark</button>
            <button onClick={async () => { const r = await fetch(`${SIDECAR}/hardware/optimize`, { method: "POST" }); const d = await r.json(); setStatus(`Optimized: ${d.applied?.join(", ") || "none"}`); }} style={{ marginLeft: 8, fontSize: 11 }}>Optimize GPU</button>

          </span>
        </div>
      )}

      {status && <div style={{ fontSize: 13, color: "var(--muted)", marginBottom: 12 }}>{status}</div>}

      {tab === "rama" && (
        <>
          <h2 style={{ marginTop: 0 }}>RAMA Training</h2>
          <div style={{ marginBottom: 16, display: "flex", alignItems: "center", gap: 12 }}>
            <label style={{ fontSize: 14 }}>
              <input type="checkbox" checked={telemetry} onChange={toggleTelemetry} /> Anonymized telemetry
            </label>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>{samples} samples</span>
            <button onClick={selfTrain} style={{ marginLeft: "auto", padding: "6px 12px", background: "var(--accent)", color: "#11111b", border: "none", borderRadius: 4, cursor: "pointer" }}>Self-train</button>
          </div>

          <h3>Manual feedback</h3>
          <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} rows={2} placeholder="Prompt" style={{ width: "100%", marginBottom: 8, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 8 }} />
          <textarea value={output} onChange={(e) => setOutput(e.target.value)} rows={2} placeholder="Output" style={{ width: "100%", marginBottom: 8, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 8 }} />
          <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 8 }}>
            <label style={{ fontSize: 13 }}>Rating</label>
            <input type="range" min={1} max={5} value={rating} onChange={(e) => setRating(Number(e.target.value))} />
            <span>{rating}</span>
          </div>
          <input value={note} onChange={(e) => setNote(e.target.value)} placeholder="Specialist (for training)" style={{ width: "100%", marginBottom: 8, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 8 }} />
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={submitFeedback} style={{ padding: "6px 12px" }}>Record feedback</button>
            <button onClick={manualTrain} style={{ padding: "6px 12px" }}>Train route</button>
          </div>

          <h3 style={{ marginTop: 24 }}>Versions</h3>
          {versions.length === 0 && <p style={{ color: "var(--muted)", fontSize: 13 }}>None yet.</p>}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {versions.map((v) => (
              <li key={v.id} style={{ display: "flex", gap: 8, alignItems: "center", padding: "4px 0", borderBottom: "1px solid var(--border)", fontSize: 13 }}>
                <code style={{ fontSize: 11 }}>{v.id}</code>
                <span style={{ color: "var(--muted)" }}>{v.label}</span>
                <button onClick={() => rollback(v.id)} style={{ marginLeft: "auto", fontSize: 11, padding: "2px 8px" }}>Restore</button>
              </li>
            ))}
          </ul>
          {versions.length > 1 && <button onClick={() => rollback()} style={{ marginTop: 8, fontSize: 12 }}>Rollback previous</button>}
        </>
      )}

      {tab === "ml" && (
        <>
          <h2 style={{ marginTop: 0 }}>ML Model Training</h2>
          <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <input value={mlName} onChange={(e) => setMlName(e.target.value)} placeholder="Model name" style={{ flex: 1, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 8 }} />
            <input type="number" min={1} max={20} value={mlEpochs} onChange={(e) => setMlEpochs(Number(e.target.value))} style={{ width: 60, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 8 }} />
            <button onClick={mlTrain} style={{ padding: "6px 12px", background: "var(--accent)", color: "#11111b", border: "none", borderRadius: 4 }}>Train</button>
          </div>
          <p style={{ fontSize: 13, color: "var(--muted)" }}>Jobs continue in the background if you leave this view.</p>
          
          
          <h3 style={{ marginTop: 16 }}>Frameworks</h3>
          <button onClick={async () => {
            const r = await fetch(`${SIDECAR}/frameworks`);
            const d = await r.json();
            const el = document.getElementById("fwList");
            if (el) el.textContent = Object.entries(d).map(([k, v]: any) => `${k}: ${v.available ? "ready" : "missing"} (train=${v.train} infer=${v.infer})`).join("\n");
          }} style={{ fontSize: 12 }}>List frameworks</button>
          
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
            {["pytorch", "tensorflow", "jax", "onnx", "numpy", "transformer", "moe", "lora"].map((fw) => (
              <button key={fw} className="fw-btn" onClick={async () => {
                setStatus(`Training ${fw}…`);
                const r = await fetch(`${SIDECAR}/frameworks/${fw}/train`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ epochs: 1 }) });
                const d = await r.json();
                setStatus(`${fw}: ${d.ok ? "ok" : d.error || "done"}`);
              }} style={{ fontSize: 11, padding: "4px 8px" }}>{fw}</button>
            ))}
          </div>

          <pre id="fwList" style={{ fontSize: 12, background: "var(--surface)", padding: 8, borderRadius: 4 }} />

          
          
          <h3 style={{ marginTop: 16 }}>RAMA states</h3>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            <button onClick={async () => { await fetch(`${SIDECAR}/rama/states/backup`, { method: "POST" }); setStatus("Backup taken"); }} style={{ fontSize: 11 }}>Backup</button>
            <button onClick={async () => { await fetch(`${SIDECAR}/rama/states/failover`, { method: "POST" }); setStatus("Failover to backup"); }} style={{ fontSize: 11 }}>Failover</button>
            <button onClick={async () => { await fetch(`${SIDECAR}/rama/states/promote`, { method: "POST" }); setStatus("Training promoted"); }} style={{ fontSize: 11 }}>Promote training</button>
            <button onClick={async () => { await fetch(`${SIDECAR}/rama/train/auto`, { method: "POST" }); setStatus("Auto-trained"); }} style={{ fontSize: 11 }}>Auto-train</button>
          </div>
          <h3 style={{ marginTop: 16 }}>Meta-models (20)</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
            {["architect","dataset","loss","optimizer","regularizer","evaluator","deployer","monitor","debugger","compressor","router","tokenizer","embedder","attention","scheduler","augmenter","aligner","safety","benchmarker","orchestrator"].map(m => (
              <button key={m} onClick={async () => { const r = await fetch(`${SIDECAR}/meta/${m}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prompt: prompt || "design" }) }); const d = await r.json(); setStatus(`${m}: ${(d.advice || "").slice(0, 50)}`); }} style={{ fontSize: 10, padding: "2px 6px" }}>{m}</button>
            ))}
          </div>

          <h3 style={{ marginTop: 16 }}>Specialist models</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {["linter", "spellcheck", "translate", "coder", "designer", "math", "science", "cad", "music", "tooluse", "art"].map((s) => (
              <button key={s} className="spec-btn" onClick={async () => {
                setStatus(`Running ${s}…`);
                const r = await fetch(`${SIDECAR}/specialist/${s}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prompt: prompt || "test" }) });
                const d = await r.json();
                setStatus(`${s}: ${(d.output || d.error || "").slice(0, 60)}`);
              }} style={{ fontSize: 11, padding: "4px 8px" }}>{s}</button>
            ))}
          </div>

          <h3 style={{ marginTop: 16 }}>Architecture</h3>
          <button onClick={async () => {
            const r = await fetch(`${SIDECAR}/diagram/${mlName || "model"}`);
            const d = await r.json();
            setStatus(d.ascii || "");
            const el = document.getElementById("diagram");
            if (el) el.innerHTML = `<pre style="font-size:12px;">${d.mermaid}</pre>`;
          }} style={{ fontSize: 12, marginBottom: 8 }}>Show diagram</button>
          <div id="diagram" style={{ background: "var(--surface)", padding: 8, borderRadius: 4, minHeight: 40 }} />

          <h3 style={{ marginTop: 16 }}>Models</h3>
          {models.length === 0 && <p style={{ color: "var(--muted)", fontSize: 13 }}>None built yet.</p>}
          <ul style={{ listStyle: "none", padding: 0 }}>
            {models.map((m: any) => (
              <li key={m.name} style={{ display: "flex", gap: 8, alignItems: "center", padding: "4px 0", borderBottom: "1px solid var(--border)", fontSize: 13 }}>
                <strong>{m.name}</strong>
                <span style={{ color: "var(--muted)" }}>{m.domain}</span>
                <span style={{ color: "var(--muted)" }}>{m.trained_epochs || 0} ep</span>
                <button onClick={async () => { await fetch(`${SIDECAR}/models/${m.name}`, { method: "DELETE" }); refresh(); }} style={{ marginLeft: "auto", fontSize: 11 }}>Delete</button>
              </li>
            ))}
          </ul>

        </>
      )}

      <h3 style={{ marginTop: 24 }}>Jobs</h3>
      {jobs.length === 0 && <p style={{ color: "var(--muted)", fontSize: 13 }}>No jobs.</p>}
      <ul style={{ listStyle: "none", padding: 0 }}>
        {jobs.map((j) => (
          <li key={j.id} style={{ display: "flex", gap: 8, alignItems: "center", padding: "4px 0", borderBottom: "1px solid var(--border)", fontSize: 13 }}>
            <code style={{ fontSize: 11 }}>{j.id}</code>
            <span>{j.kind}</span>
            <span style={{ color: j.status === "done" ? "var(--ok)" : j.status === "failed" ? "var(--bad)" : "var(--muted)" }}>{j.status}</span>
            <span style={{ marginLeft: "auto" }}>{Math.round(j.progress * 100)}%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
