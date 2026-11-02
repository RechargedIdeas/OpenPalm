interface ModelCard {
  name: string;
  params: string;
  tokensPerSec: string;
  ram: string;
  explanation: string;
}

const CANDIDATES: ModelCard[] = [
  {
    name: "Phi-4-mini",
    params: "3.8B",
    tokensPerSec: "~20 tok/s",
    ram: "2.5 GB",
    explanation: "This model runs on your computer. Writing an email takes about 10 seconds.",
  },
  {
    name: "Qwen3 1.7B",
    params: "1.7B",
    tokensPerSec: "~30 tok/s",
    ram: "1.2 GB",
    explanation: "Faster and smaller. Good if other apps are open.",
  },
  {
    name: "Llama 3.1 8B",
    params: "8B",
    tokensPerSec: "~8 tok/s",
    ram: "5 GB",
    explanation: "Higher quality writing. May be tight on 8 GB machines.",
  },
];

interface HardwareCardProps {
  onSelect?: (name: string) => void;
}

export function HardwareCard({ onSelect }: HardwareCardProps) {
  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginTop: 0 }}>Recommended models</h2>
      <p style={{ color: "#a6adc8", marginBottom: 16 }}>
        Based on a simulated scan: 8 GB RAM, Intel iGPU, no dedicated GPU. Recommended: Phi-4-mini.
      </p>
      <div style={{ display: "grid", gap: 12 }}>
        {CANDIDATES.map((m) => (
          <div
            key={m.name}
            style={{
              padding: 16,
              background: "#1e1e2e",
              border: "1px solid #313244",
              borderRadius: 6,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <strong>{m.name}</strong>
              <span style={{ fontSize: 13, color: "#a6adc8" }}>{m.params}</span>
            </div>
            <div style={{ fontSize: 13, color: "#a6adc8", margin: "4px 0" }}>
              {m.tokensPerSec} · {m.ram}
            </div>
            <p style={{ margin: "8px 0", fontSize: 14 }}>{m.explanation}</p>
            <button
              onClick={() => onSelect?.(m.name)}
              style={{
                padding: "6px 12px",
                background: "#89b4fa",
                color: "#11111b",
                border: "none",
                borderRadius: 4,
                cursor: "pointer",
              }}
            >
              Download and test
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
