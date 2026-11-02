import { useState } from "react";

export interface Claim {
  text: string;
  status: "SUPPORTED" | "UNSUPPORTED" | "UNCERTAIN";
  source?: string;
}

interface VerificationTableProps {
  claims: Claim[];
  onFix?: (index: number) => void;
}

export function VerificationTable({ claims, onFix }: VerificationTableProps) {
  const [open, setOpen] = useState(true);

  if (claims.length === 0) return null;

  const hasUnsupported = claims.some((c) => c.status === "UNSUPPORTED");

  return (
    <div style={{ marginTop: 12, border: "1px solid var(--border)", borderRadius: 6, overflow: "hidden" }}>
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          width: "100%",
          padding: "8px 12px",
          background: "var(--surface)",
          border: "none",
          color: "var(--text)",
          textAlign: "left",
          cursor: "pointer",
          fontSize: 13,
        }}
      >
        Verification {open ? "▾" : "▸"} {hasUnsupported ? "— claims need review" : "— all supported"}
      </button>
      {open && (
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "var(--surface-2)" }}>
              <th style={{ textAlign: "left", padding: "6px 12px" }}>Claim</th>
              <th style={{ textAlign: "left", padding: "6px 12px" }}>Status</th>
              <th style={{ textAlign: "left", padding: "6px 12px" }}>Source</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {claims.map((c, i) => (
              <tr key={i} style={{ borderTop: "1px solid var(--border)" }}>
                <td style={{ padding: "6px 12px" }}>{c.text}</td>
                <td style={{ padding: "6px 12px", color: c.status === "SUPPORTED" ? "var(--ok)" : c.status === "UNSUPPORTED" ? "var(--bad)" : "#f9e2af" }}>
                  {c.status === "SUPPORTED" ? "✓" : c.status === "UNSUPPORTED" ? "✗" : "?"} {c.status}
                </td>
                <td style={{ padding: "6px 12px", color: "var(--muted)" }}>{c.source || "—"}</td>
                <td style={{ padding: "6px 12px" }}>
                  {c.status === "UNSUPPORTED" && onFix && (
                    <button onClick={() => onFix(i)} style={{ fontSize: 12, padding: "2px 8px" }}>Fix</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
