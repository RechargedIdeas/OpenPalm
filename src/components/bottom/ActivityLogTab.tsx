import { useState } from "react";

const SAMPLE_EVENTS = [
  { time: "14:02:11", level: "info", msg: "Indexed 14 files from Documents/Listings" },
  { time: "14:02:14", level: "info", msg: "Model loaded in 4.2s" },
  { time: "14:03:01", level: "warn", msg: "Email sync delayed — retrying" },
  { time: "14:03:08", level: "info", msg: "Verification pass 2 complete" },
];

export function ActivityLogTab() {
  const [events] = useState(SAMPLE_EVENTS);

  return (
    <div style={{ height: "100%", overflow: "auto", padding: 8, fontFamily: "ui-monospace, monospace", fontSize: 12 }}>
      {events.map((e, i) => (
        <div key={i} style={{ marginBottom: 4, color: e.level === "warn" ? "#f9e2af" : "#a6adc8" }}>
          <span style={{ color: "#585b70" }}>{e.time}</span>{" "}
          <span style={{ color: e.level === "warn" ? "#f9e2af" : "#89b4fa" }}>[{e.level}]</span>{" "}
          {e.msg}
        </div>
      ))}
      <div style={{ marginTop: 12, color: "#585b70", fontStyle: "italic" }}>
        (stub) — real events will stream from the Rust logger
      </div>
    </div>
  );
}
