import { useEffect, useState } from "react";

const BASE = "http://127.0.0.1:8765";

export function ServerControl() {
  const [running, setRunning] = useState(false);
  const [pid, setPid] = useState<number | null>(null);
  const [msg, setMsg] = useState("checking…");

  const refresh = async () => {
    try {
      const r = await fetch(`${BASE}/control/status`);
      const s = await r.json();
      setRunning(!!s.running);
      setPid(s.pid ?? null);
      setMsg(s.running ? `running (pid ${s.pid})` : "stopped");
    } catch {
      setMsg("unreachable");
      setRunning(false);
    }
  };

  const act = async (path: string) => {
    try {
      await fetch(`${BASE}${path}`, { method: "POST" });
    } catch {
      /* ignore */
    }
    setTimeout(refresh, 700);
  };

  useEffect(() => {
    (async () => {
      await refresh();
      try {
        const r = await fetch(`${BASE}/control/status`);
        const s = await r.json();
        if (!s.running) await act("/control/start");
      } catch {
        /* server may not be up yet */
      }
    })();
    const id = setInterval(refresh, 4000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13 }}>
      <span style={{ width: 10, height: 10, borderRadius: "50%", background: running ? "#a6e3a1" : "#585b70" }} />
      <span>{msg}</span>
      <button onClick={() => act("/control/start")} disabled={running}>Start</button>
      <button onClick={() => act("/control/stop")} disabled={!running}>Stop</button>
      <button onClick={() => act("/control/reset")}>Reset</button>
    </div>
  );
}
