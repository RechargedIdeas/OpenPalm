export function ToolCallChip({ label }: { label: string }) {
  return (
    <span style={{ display: "inline-block", background: "#313244", color: "#cdd6f4", fontSize: 12, padding: "2px 8px", borderRadius: 12, marginRight: 6 }}>
      🔧 {label}
    </span>
  );
}
