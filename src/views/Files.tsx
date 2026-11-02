import { useState } from "react";
import { HardwareCard } from "./onboarding/HardwareCard";

export function FilesView() {
  const [folders, setFolders] = useState<string[]>([]);
  const [status, setStatus] = useState("");

  const addFolder = () => {
    const name = window.prompt("Folder path (stub):", "Documents/Listings");
    if (name) {
      setFolders((f) => [...f, name]);
      setStatus(`Indexing ${name}… (stub)`);
      setTimeout(() => setStatus(`${name} indexed. Searchable.`), 800);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2 style={{ marginTop: 0 }}>Files</h2>
      <p style={{ color: "#a6adc8" }}>
        Add folders of PDFs, CSVs, and notes. Supported: PDF, CSV, TXT, EML. Scans are OCR’d.
      </p>
      <button
        onClick={addFolder}
        style={{
          padding: "8px 16px",
          background: "#89b4fa",
          color: "#11111b",
          border: "none",
          borderRadius: 4,
          cursor: "pointer",
          marginBottom: 16,
        }}
      >
        Add folder
      </button>
      {status && <div style={{ fontSize: 13, color: "#a6e3a1", marginBottom: 12 }}>{status}</div>}
      <ul style={{ paddingLeft: 20 }}>
        {folders.map((f) => (
          <li key={f}>{f}</li>
        ))}
      </ul>
      {folders.length === 0 && (
        <p style={{ color: "#a6adc8" }}>No folders indexed yet.</p>
      )}
      <div style={{ marginTop: 32 }}>
        <HardwareCard />
      </div>
    </div>
  );
}
