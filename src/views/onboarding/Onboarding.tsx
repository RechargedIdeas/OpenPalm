import { useState } from "react";
import { HardwareCard } from "./HardwareCard";

export function Onboarding() {
  const [step, setStep] = useState<"welcome" | "model" | "done">("welcome");

  if (step === "done") {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <h2>Ready</h2>
        <p style={{ color: "#a6adc8" }}>You can start chatting. Every response is checked against your sources.</p>
      </div>
    );
  }

  if (step === "model") {
    return (
      <div>
        <HardwareCard onSelect={() => setStep("done")} />
        <div style={{ padding: "0 24px 24px" }}>
          <button onClick={() => setStep("done")} style={{ padding: "8px 16px", background: "#313244", border: "none", color: "#cdd6f4", borderRadius: 4 }}>
            Skip for now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: 40, maxWidth: 520, margin: "0 auto", textAlign: "center" }}>
      <h1 style={{ marginBottom: 8 }}>OpenPalm</h1>
      <p style={{ color: "#a6adc8", marginBottom: 24 }}>
        A local-first assistant for real estate. Your data stays on this machine unless you choose a cloud model.
      </p>
      <button
        onClick={() => setStep("model")}
        style={{ padding: "10px 24px", background: "#89b4fa", color: "#11111b", border: "none", borderRadius: 6, fontSize: 16, cursor: "pointer" }}
      >
        Get started
      </button>
    </div>
  );
}
