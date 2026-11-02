import { useEffect, useRef, useState } from "react";

export function TerminalTab() {
  const [lines, setLines] = useState<string[]>(["agent@harness:~$ "]);
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  const submit = () => {
    const cmd = input.trim();
    if (!cmd) return;
    setLines((l) => [...l, `agent@harness:~$ ${cmd}`, `  (stub) command not executed — PTY deferred`]);
    setInput("");
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", background: "#11111b", fontFamily: "ui-monospace, monospace", fontSize: 13 }}>
      <div style={{ flex: 1, overflow: "auto", padding: 8 }}>
        {lines.map((line, i) => (
          <div key={i} style={{ whiteSpace: "pre-wrap" }}>{line}</div>
        ))}
        <div ref={endRef} />
      </div>
      <div style={{ display: "flex", borderTop: "1px solid #313244" }}>
        <span style={{ padding: "6px 8px", color: "#a6e3a1" }}>$</span>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          style={{ flex: 1, background: "transparent", border: "none", color: "#cdd6f4", outline: "none", fontFamily: "inherit", fontSize: "inherit" }}
          placeholder="type a command…"
        />
      </div>
    </div>
  );
}
