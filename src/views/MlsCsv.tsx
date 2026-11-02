import { useState } from "react";

const SAMPLE_ROWS = [
  { address: "123 Main St", sqft: 2140, price: 485000, beds: 4 },
  { address: "456 Oak Ave", sqft: 1800, price: 420000, beds: 3 },
  { address: "789 Pine Rd", sqft: 3200, price: 610000, beds: 5 },
  { address: "101 Elm St", sqft: 1500, price: 390000, beds: 3 },
];

export function MlsCsvView() {
  const [rows, setRows] = useState(SAMPLE_ROWS);
  const [sorted, setSorted] = useState(false);

  const sortAndFlag = () => {
    const avg = rows.reduce((s, r) => s + r.price / r.sqft, 0) / rows.length;
    const next = [...rows]
      .map((r) => ({ ...r, outlier: Math.abs(r.price / r.sqft - avg) / avg > 0.15 }))
      .sort((a, b) => b.sqft - a.sqft);
    setRows(next);
    setSorted(true);
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginTop: 0 }}>MLS / CSV</h2>
      <p style={{ color: "#a6adc8" }}>Upload an MLS export. Sample data is loaded.</p>
      <button
        onClick={sortAndFlag}
        style={{ padding: "8px 16px", background: "#89b4fa", color: "#11111b", border: "none", borderRadius: 4, cursor: "pointer", marginBottom: 12 }}
      >
        Sort by sqft and flag outliers
      </button>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #313244" }}>
            <th style={{ textAlign: "left", padding: 6 }}>Address</th>
            <th style={{ textAlign: "right", padding: 6 }}>Sqft</th>
            <th style={{ textAlign: "right", padding: 6 }}>Price</th>
            <th style={{ textAlign: "right", padding: 6 }}>Beds</th>
            {sorted && <th style={{ textAlign: "left", padding: 6 }}>Flag</th>}
          </tr>
        </thead>
        <tbody>
          {rows.map((r: any, i) => (
            <tr key={i} style={{ borderBottom: "1px solid #313244" }}>
              <td style={{ padding: 6 }}>{r.address}</td>
              <td style={{ padding: 6, textAlign: "right" }}>{r.sqft}</td>
              <td style={{ padding: 6, textAlign: "right" }}>${r.price.toLocaleString()}</td>
              <td style={{ padding: 6, textAlign: "right" }}>{r.beds}</td>
              {sorted && <td style={{ padding: 6, color: r.outlier ? "#f38ba8" : "#a6e3a1" }}>{r.outlier ? "Outlier" : "OK"}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
