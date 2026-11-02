import { ReactNode } from "react";

interface EmptyStateProps {
  title: string;
  description: string;
  guideLink?: string;
}

export function EmptyState({ title, description, guideLink = "#" }: EmptyStateProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        height: "100%",
        color: "#a6adc8",
        textAlign: "center",
        padding: 40,
      }}
    >
      <h2 style={{ margin: "0 0 8px", color: "#cdd6f4", fontSize: 20 }}>{title}</h2>
      <p style={{ margin: "0 0 16px", maxWidth: 360 }}>{description}</p>
      <a href={guideLink} style={{ color: "#89b4fa", textDecoration: "none" }}>
        Read the guide →
      </a>
    </div>
  );
}
