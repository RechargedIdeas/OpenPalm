import { useState, useRef } from "react";
import { SlashPicker } from "./SlashPicker";
import { parseCommand, SlashCommand } from "../../lib/commands/registry";

interface ChatInputProps {
  onSend: (text: string) => void;
  onCommand?: (name: string, args: string[]) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, onCommand, disabled }: ChatInputProps) {
  const [text, setText] = useState("");
  const [showPicker, setShowPicker] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const query = text.startsWith("/") ? text.slice(1).split(/\s/)[0] : "";

  const handleChange = (v: string) => {
    setText(v);
    setShowPicker(v.startsWith("/") && !v.includes(" "));
  };

  const selectCommand = (cmd: SlashCommand) => {
    const hint = cmd.args ? ` ${cmd.args}` : "";
    setText(`/${cmd.name}${hint}`);
    setShowPicker(false);
    inputRef.current?.focus();
  };

  const submit = () => {
    if (!text.trim() || disabled) return;
    const parsed = parseCommand(text);
    if (parsed && onCommand) {
      onCommand(parsed.name, parsed.args);
    } else {
      onSend(text.trim());
    }
    setText("");
    setShowPicker(false);
  };

  return (
    <div style={{ borderTop: "1px solid #313244", padding: 12, position: "relative" }}>
      {showPicker && (
        <SlashPicker
          query={query}
          onSelect={selectCommand}
          onDismiss={() => setShowPicker(false)}
        />
      )}
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <button style={{ fontSize: 12, padding: "4px 8px", background: "#313244", border: "none", color: "#cdd6f4", borderRadius: 4 }}>Summarize email</button>
        <button style={{ fontSize: 12, padding: "4px 8px", background: "#313244", border: "none", color: "#cdd6f4", borderRadius: 4 }}>Find contract</button>
        <button style={{ fontSize: 12, padding: "4px 8px", background: "#313244", border: "none", color: "#cdd6f4", borderRadius: 4 }}>Chart prices</button>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <textarea
          ref={inputRef}
          value={text}
          onChange={(e) => handleChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey && !showPicker) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Type a message… or / for commands"
          rows={2}
          disabled={disabled}
          style={{ flex: 1, background: "#1e1e2e", color: "#cdd6f4", border: "1px solid #45475a", borderRadius: 6, padding: 8, resize: "none" }}
        />
        <button onClick={submit} disabled={disabled || !text.trim()} style={{ padding: "0 16px", background: "#89b4fa", color: "#11111b", border: "none", borderRadius: 6, cursor: "pointer" }}>
          Send
        </button>
      </div>
    </div>
  );
}
