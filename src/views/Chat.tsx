import { useState, useEffect } from "react";
import { ChatInput } from "../components/chat/ChatInput";
import { VerificationTable, Claim } from "../components/verification/VerificationTable";
import { VerificationSlider } from "../components/verification/VerificationSlider";
import { useUI } from "../stores/ui";
import { sendChat } from "../api/sidecar";

interface Message {
  role: "user" | "agent";
  content: string;
  claims?: Claim[];
}

const STORAGE_KEY = "openpalm-chat";
const SETTINGS_KEY = "openpalm-settings";

function loadMessages(): Message[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function loadSettings() {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    return raw ? JSON.parse(raw) : { model: "phi4-mini", passes: 2 };
  } catch {
    return { model: "phi4-mini", passes: 2 };
  }
}


const SIDECAR = "http://127.0.0.1:8765";

async function loadShared(): Promise<{ messages: Message[]; settings: { model: string; passes: number }; sources: string } | null> {
  try {
    const r = await fetch(`${SIDECAR}/data`);
    if (r.ok) return await r.json();
  } catch {}
  return null;
}

async function saveSharedMessages(messages: Message[]) {
  try {
    await fetch(`${SIDECAR}/data/messages`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages }),
    });
  } catch {}
}

async function saveSharedSettings(model: string, passes: number) {
  try {
    await fetch(`${SIDECAR}/data/settings`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, passes }),
    });
  } catch {}
}

async function saveSharedSources(sources: string) {
  try {
    await fetch(`${SIDECAR}/data/sources`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sources }),
    });
  } catch {}
}

export function ChatView() {
  const [messages, setMessages] = useState<Message[]>(loadMessages);
  const [passes, setPasses] = useState(loadSettings().passes);
  const [model, setModel] = useState(loadSettings().model);
  const [sources, setSources] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const { setActiveView, setBottomTab, setDebugEnabled, setBottomCollapsed, debugEnabled } = useUI();

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch {}
  }, [messages]);

  useEffect(() => {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify({ model, passes }));
      saveSharedSettings(model, passes);
    } catch {}
  }, [model, passes]);

  const handleCommand = (name: string, args: string[]) => {
    switch (name) {
      case "clear":
        setMessages([]);
        break;
      case "facts": {
        const n = parseInt(args[0] || "2", 10);
        if (n >= 1 && n <= 5) setPasses(n);
        break;
      }
      case "files":
        setActiveView("files");
        break;
      case "email":
        setActiveView("email");
        break;
      case "debug":
        setDebugEnabled(!debugEnabled);
        setBottomTab("debug");
        setBottomCollapsed(false);
        break;
      default:
        break;
    }
  };

  const send = async (text: string) => {
    setMessages((m) => [...m, { role: "user", content: text }]);
    setBusy(true);
    try {
      const srcList = sources.trim() ? sources.split("\n---\n").map((s) => s.trim()).filter(Boolean) : [text];
      const res = await sendChat(text, srcList, passes, model);
      setMessages((m) => [...m, { role: "agent", content: res.draft, claims: res.claims }]);
    } catch {
      setMessages((m) => [...m, { role: "agent", content: "Could not reach the sidecar. Check that it is running." }]);
    } finally {
      setBusy(false);
    }
  };

  const fix = (idx: number) => {
    setMessages((m) =>
      m.map((msg) =>
        msg.claims
          ? {
              ...msg,
              claims: msg.claims.map((c, i) =>
                i === idx ? { ...c, status: "SUPPORTED" as const, source: "Corrected by you" } : c
              ),
            }
          : msg
      )
    );
  };

  const lastAgent = [...messages].reverse().find((m) => m.role === "agent");
  const hasUnsupported = messages.some((m) => m.claims?.some((c) => c.status === "UNSUPPORTED"));

  const copyLast = async () => {
    if (!lastAgent || hasUnsupported) return;
    try {
      await navigator.clipboard.writeText(lastAgent.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard denied */
    }
  };


  const sendFeedback = async (rating: number) => {
    const last = messages.filter((m) => m.role === "agent").pop();
    const prev = messages.filter((m) => m.role === "user").pop();
    if (!last || !prev) return;
    try {
      await fetch(`${SIDECAR}/rama/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: prev.content, output: last.content, rating }),
      });
    } catch {}
  };

  const newChat = () => {
    if (messages.length && !window.confirm("Start a new chat? Current history will be cleared.")) return;
    setMessages([]);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{ padding: "8px 16px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 12 }}>
        <VerificationSlider value={passes} onChange={setPasses} />
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          style={{ background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: "2px 6px", fontSize: 13 }}
        >
          <option value="phi4-mini">Phi-4-mini</option>
          <option value="qwen3-1.7b">Qwen3 1.7B</option>
          <option value="llama3.2-1b">Llama 3.2 1B</option>
        </select>
        <button onClick={newChat} style={{ marginLeft: "auto", fontSize: 12, padding: "4px 10px" }}>
          New chat
        </button>
      </div>
      
      <div style={{ padding: "4px 16px", fontSize: 12, color: "var(--muted)", borderBottom: "1px solid var(--border)" }}>
        Model: {model} · Passes: {passes} · Sources: {sources.trim() ? "set" : "none (claims checked against your message)"}
      </div>
      <div style={{ padding: "8px 16px", borderBottom: "1px solid var(--border)" }}>
        <label style={{ fontSize: 12, color: "var(--muted)" }}>
          Sources (paste your documents, separate with ---)
          <textarea
            value={sources}
            onChange={(e) => { setSources(e.target.value); saveSharedSources(e.target.value); }}
            rows={2}
            placeholder="Paste notes, listings, or emails here so claims can be checked against them…"
            style={{ display: "block", width: "100%", marginTop: 4, background: "var(--surface)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 4, padding: 6, fontSize: 13, resize: "vertical" }}
          />
        </label>
      </div>
      <div style={{ flex: 1, overflow: "auto", padding: 16 }}>
        {messages.length === 0 && (
          <div style={{ color: "var(--muted)", textAlign: "center", marginTop: 40, maxWidth: 480, marginLeft: "auto", marginRight: "auto" }}>
            <p>Paste your notes above, then ask OpenPalm to draft or check something.</p>
            <p style={{ fontSize: 13, marginTop: 16 }}>Examples:</p>
            <ul style={{ textAlign: "left", fontSize: 13, lineHeight: 1.6 }}>
              <li>Write a short bio from my notes</li>
              <li>Summarize this email for a parent</li>
              <li>Check this paragraph against my lab notes</li>
            </ul>
          </div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 4 }}>{m.role === "user" ? "You" : "Agent"}</div>
            <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
            {m.claims && <VerificationTable claims={m.claims} onFix={fix} />}
          </div>
        ))}
        {busy && <div style={{ color: "var(--muted)" }}>Thinking…</div>}
      </div>
      <div style={{ padding: "0 16px 8px", display: "flex", gap: 8, justifyContent: "flex-end", alignItems: "center" }}>
        {hasUnsupported && <span style={{ fontSize: 12, color: "var(--bad)", marginRight: "auto" }}>Fix unsupported claims before copying</span>}
        <button
          disabled={hasUnsupported || !lastAgent}
          onClick={copyLast}
          style={{ padding: "6px 12px", opacity: hasUnsupported || !lastAgent ? 0.4 : 1 }}
        >
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <ChatInput onSend={send} onCommand={handleCommand} disabled={busy} />
    </div>
  );
}
