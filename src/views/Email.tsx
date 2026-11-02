import { useState } from "react";

const SAMPLE_MAIL = [
  { from: "seller@example.com", subject: "Pre-approval attached", date: "2026-10-28" },
  { from: "buyer@example.com", subject: "Showing request for 123 Main", date: "2026-10-29" },
  { from: "lender@example.com", subject: "Rate lock confirmation", date: "2026-10-27" },
];

export function EmailView() {
  const [connected, setConnected] = useState(false);
  const [query, setQuery] = useState("");
  const results = SAMPLE_MAIL.filter(
    (m) => !query || m.subject.toLowerCase().includes(query.toLowerCase()) || m.from.includes(query)
  );

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginTop: 0 }}>Email</h2>
      {!connected ? (
        <div>
          <p style={{ color: "#a6adc8" }}>Connect Gmail, Outlook, or IMAP. Messages stay on this machine.</p>
          <button
            onClick={() => setConnected(true)}
            style={{ padding: "8px 16px", background: "#89b4fa", color: "#11111b", border: "none", borderRadius: 4, cursor: "pointer" }}
          >
            Connect email (stub)
          </button>
        </div>
      ) : (
        <div>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search subject or sender…"
            style={{ width: "100%", maxWidth: 400, padding: 8, background: "#1e1e2e", color: "#cdd6f4", border: "1px solid #45475a", borderRadius: 4, marginBottom: 12 }}
          />
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #313244" }}>
                <th style={{ textAlign: "left", padding: 6 }}>From</th>
                <th style={{ textAlign: "left", padding: 6 }}>Subject</th>
                <th style={{ textAlign: "left", padding: 6 }}>Date</th>
              </tr>
            </thead>
            <tbody>
              {results.map((m, i) => (
                <tr key={i} style={{ borderBottom: "1px solid #313244" }}>
                  <td style={{ padding: 6 }}>{m.from}</td>
                  <td style={{ padding: 6 }}>{m.subject}</td>
                  <td style={{ padding: 6 }}>{m.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
