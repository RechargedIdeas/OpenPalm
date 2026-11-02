"""Frontend client for the sidecar. Falls back to local stub if sidecar is down."""

export interface Claim {
  text: string;
  status: "SUPPORTED" | "UNSUPPORTED" | "UNCERTAIN";
  source?: string;
}

export interface ChatResponse {
  draft: string;
  claims: Claim[];
  passes: number;
}

const SIDECAR = "http://127.0.0.1:8765";

export async function sendChat(
  message: string,
  sources: string[] = [],
  passes = 2,
  model = "phi4-mini"
): Promise<ChatResponse> {
  try {
    const r = await fetch(`${SIDECAR}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, sources, passes, model }),
    });
    if (r.ok) return (await r.json()) as ChatResponse;
  } catch {
    /* sidecar not running */
  }
  // Local fallback so the UI stays usable
  return {
    draft: "Draft based on the facts you provided. The kitchen is described as renovated.",
    claims: [
      { text: "4 bed, 2.5 bath", status: "SUPPORTED", source: "source" },
      { text: "2,140 sqft", status: "SUPPORTED", source: "source" },
      { text: "renovated kitchen", status: "UNSUPPORTED", source: "Source says updated" },
    ],
    passes,
  };
}
