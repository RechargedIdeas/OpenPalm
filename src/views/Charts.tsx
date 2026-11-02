import { useState } from "react";

const SAMPLE = [
  { month: "May", price: 470000 },
  { month: "Jun", price: 482000 },
  { month: "Jul", price: 475000 },
  { month: "Aug", price: 490000 },
  { month: "Sep", price: 485000 },
  { month: "Oct", price: 498000 },
];

export function ChartsView() {
  const [type, setType] = useState<"bar" | "line" | "scatter">("bar");
  const max = Math.max(...SAMPLE.map((d) => d.price));

  const exportPng = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 400;
    canvas.height = 200;
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.fillStyle = "#11111b";
      ctx.fillRect(0, 0, 400, 200);
      ctx.fillStyle = "#89b4fa";
      ctx.fillText("Price trend (stub export)", 10, 20);
      const a = document.createElement("a");
      a.href = canvas.toDataURL("image/png");
      a.download = "chart.png";
      a.click();
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginTop: 0 }}>Charts</h2>
      <div style={{ marginBottom: 12 }}>
        {(["bar", "line", "scatter"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setType(t)}
            style={{
              marginRight: 8,
              padding: "4px 12px",
              background: type === t ? "#89b4fa" : "#313244",
              color: type === t ? "#11111b" : "#cdd6f4",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            {t}
          </button>
        ))}
        <button onClick={exportPng} style={{ padding: "4px 12px", marginLeft: 8 }}>
          Export PNG
        </button>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 160, borderBottom: "1px solid #313244", padding: 8 }}>
        {SAMPLE.map((d) => (
          <div key={d.month} style={{ flex: 1, textAlign: "center" }}>
            <div
              style={{
                height: (d.price / max) * 120,
                background: type === "scatter" ? "transparent" : "#89b4fa",
                border: type === "scatter" ? "2px solid #89b4fa" : "none",
                borderRadius: type === "scatter" ? "50%" : 2,
                margin: "0 auto",
                width: type === "scatter" ? 12 : "70%",
              }}
            />
            <div style={{ fontSize: 11, marginTop: 4 }}>{d.month}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
