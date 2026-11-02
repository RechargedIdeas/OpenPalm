import { useEffect, useRef, useState } from "react";
import { COMMANDS, filterCommands, SlashCommand } from "../../lib/commands/registry";

interface SlashPickerProps {
  query: string;
  onSelect: (cmd: SlashCommand) => void;
  onDismiss: () => void;
}

export function SlashPicker({ query, onSelect, onDismiss }: SlashPickerProps) {
  const matches = filterCommands(query);
  const [index, setIndex] = useState(0);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setIndex(0);
  }, [query]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setIndex((i) => Math.min(i + 1, matches.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault();
        if (matches[index]) onSelect(matches[index]);
      } else if (e.key === "Escape") {
        e.preventDefault();
        onDismiss();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [matches, index, onSelect, onDismiss]);

  if (matches.length === 0) return null;

  return (
    <div
      ref={listRef}
      style={{
        position: "absolute",
        bottom: "100%",
        left: 0,
        right: 0,
        background: "#1e1e2e",
        border: "1px solid #45475a",
        borderRadius: 6,
        maxHeight: 200,
        overflow: "auto",
        zIndex: 10,
        marginBottom: 4,
      }}
    >
      {matches.map((cmd, i) => (
        <div
          key={cmd.name}
          onClick={() => onSelect(cmd)}
          style={{
            padding: "6px 12px",
            background: i === index ? "#313244" : "transparent",
            cursor: "pointer",
            display: "flex",
            justifyContent: "space-between",
            fontSize: 13,
          }}
        >
          <span>
            <strong>/{cmd.name}</strong>
            {cmd.args && <span style={{ color: "#a6adc8", marginLeft: 6 }}>{cmd.args}</span>}
          </span>
          <span style={{ color: "#a6adc8", fontSize: 12 }}>{cmd.description}</span>
        </div>
      ))}
    </div>
  );
}
