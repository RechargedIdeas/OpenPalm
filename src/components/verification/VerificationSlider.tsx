interface VerificationSliderProps {
  value: number;
  onChange: (n: number) => void;
}

export function VerificationSlider({ value, onChange }: VerificationSliderProps) {
  const labels = ["Fast (1)", "Standard (2)", "Strict (3)"];
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, fontSize: 13, color: "#a6adc8" }}>
      <span>Fact check:</span>
      <input
        type="range"
        min={1}
        max={3}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        style={{ width: 80 }}
      />
      <span>{labels[value - 1]}</span>
      <span style={{ fontSize: 12 }}>Each extra pass catches more errors.</span>
    </div>
  );
}
