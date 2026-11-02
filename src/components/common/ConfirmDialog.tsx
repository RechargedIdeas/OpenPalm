import { useState } from "react";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  body: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({ open, title, body, onConfirm, onCancel }: ConfirmDialogProps) {
  if (!open) return null;
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 200,
      }}
    >
      <div style={{ background: "#1e1e2e", padding: 24, borderRadius: 8, maxWidth: 400, border: "1px solid #313244" }}>
        <h3 style={{ marginTop: 0 }}>{title}</h3>
        <p style={{ color: "#a6adc8", fontSize: 14 }}>{body}</p>
        <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 16 }}>
          <button onClick={onCancel} style={{ padding: "6px 12px", background: "#313244", border: "none", color: "#cdd6f4", borderRadius: 4 }}>
            Cancel
          </button>
          <button onClick={onConfirm} style={{ padding: "6px 12px", background: "#89b4fa", border: "none", color: "#11111b", borderRadius: 4 }}>
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}

export function useConfirm() {
  const [state, setState] = useState<{ open: boolean; title: string; body: string; resolve?: (v: boolean) => void }>({
    open: false,
    title: "",
    body: "",
  });

  const confirm = (title: string, body: string) =>
    new Promise<boolean>((resolve) => {
      setState({ open: true, title, body, resolve });
    });

  const onConfirm = () => {
    state.resolve?.(true);
    setState((s) => ({ ...s, open: false }));
  };
  const onCancel = () => {
    state.resolve?.(false);
    setState((s) => ({ ...s, open: false }));
  };

  return { confirm, dialog: <ConfirmDialog open={state.open} title={state.title} body={state.body} onConfirm={onConfirm} onCancel={onCancel} /> };
}
