/** Complete sidecar API client. Every backend endpoint in one place. */

const BASE = "http://127.0.0.1:8765";

async function req<T = any>(path: string, opts: RequestInit = {}): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!r.ok) throw new Error(`${path} ${r.status}`);
  return r.json();
}

export const api = {
  // Chat
  chat: (message: string, sources: string[] = [], passes = 2, model = "phi4-mini") =>
    req("/chat", { method: "POST", body: JSON.stringify({ message, sources, passes, model }) }),
  health: () => req("/health"),

  // Server
  controlStatus: () => req("/control/status"),
  controlStart: () => req("/control/start", { method: "POST" }),
  controlStop: () => req("/control/stop", { method: "POST" }),
  controlReset: () => req("/control/reset", { method: "POST" }),

  // Data
  getData: () => req("/data"),
  putMessages: (messages: any[]) => req("/data/messages", { method: "PUT", body: JSON.stringify({ messages }) }),
  putSettings: (settings: any) => req("/data/settings", { method: "PUT", body: JSON.stringify(settings) }),
  putSources: (sources: string) => req("/data/sources", { method: "PUT", body: JSON.stringify({ sources }) }),

  // Pairing
  pairCode: () => req("/pair/code"),
  pairRedeem: (code: string) => req("/pair/redeem", { method: "POST", body: JSON.stringify({ code }) }),
  pairStatus: () => req("/pair/status"),

  // Models & specialists
  models: () => req("/models"),
  specialist: (name: string, prompt: string, model?: string) =>
    req(`/specialist/${name}`, { method: "POST", body: JSON.stringify({ prompt, model }) }),
  modelsList: () => req("/models/list"),
  modelsDelete: (name: string) => req(`/models/${name}`, { method: "DELETE" }),

  // RAMA
  rama: (prompt: string, mode = "auto") => req("/rama", { method: "POST", body: JSON.stringify({ prompt, mode }) }),
  ramaFeedback: (prompt: string, output: string, rating: number, note = "") =>
    req("/rama/feedback", { method: "POST", body: JSON.stringify({ prompt, output, rating, note }) }),
  ramaVersions: () => req("/rama/versions"),
  ramaRollback: (id?: string) => req("/rama/rollback", { method: "POST", body: JSON.stringify({ id }) }),

  // Training
  trainStatus: () => req("/train/status"),
  trainTelemetry: (enabled: boolean) => req("/train/telemetry", { method: "POST", body: JSON.stringify({ enabled }) }),
  trainSelf: () => req("/train/self", { method: "POST" }),
  trainManual: (prompt: string, specialist: string) =>
    req("/train/manual", { method: "POST", body: JSON.stringify({ prompt, specialist }) }),
  trainMl: (name: string, epochs: number) => req("/train/ml", { method: "POST", body: JSON.stringify({ name, epochs }) }),
  trainJob: (jid: string) => req(`/train/job/${jid}`),
  trainConfig: (workers: number, batch_size: number) =>
    req("/train/config", { method: "POST", body: JSON.stringify({ workers, batch_size }) }),
  trainStop: () => req("/train/stop", { method: "POST" }),
  trainStopCurrent: () => req("/train/stop/current", { method: "POST" }),
  trainMain: (steps = 5) => req("/train/main", { method: "POST", body: JSON.stringify({ steps }) }),

  // ML build
  mlBuild: (name: string, domain: string, system_prompt: string) =>
    req("/ml/build", { method: "POST", body: JSON.stringify({ name, domain, system_prompt }) }),
  mlTrain: (name: string, epochs: number) => req("/ml/train", { method: "POST", body: JSON.stringify({ name, epochs }) }),

  // Hardware & metrics
  hardware: () => req("/hardware"),
  hardwareBench: () => req("/hardware/bench", { method: "POST" }),
  hardwareOptimize: () => req("/hardware/optimize", { method: "POST" }),
  hardwareVram: () => req("/hardware/vram", { method: "POST" }),
  metrics: () => req("/metrics"),
  backends: () => req("/backends"),
  frameworks: () => req("/frameworks"),
  frameworkTrain: (name: string, epochs = 1) =>
    req(`/frameworks/${name}/train`, { method: "POST", body: JSON.stringify({ epochs }) }),
  frameworkInfer: (name: string, inputs: any) =>
    req(`/frameworks/${name}/infer`, { method: "POST", body: JSON.stringify({ inputs }) }),

  // Snapshots & telemetry
  snapshots: () => req("/snapshots"),
  snapshot: (state: any, label = "") => req("/snapshot", { method: "POST", body: JSON.stringify({ state, label }) }),
  telemetry: () => req("/telemetry"),
  diagram: (name: string) => req(`/diagram/${name}`),

  // Unified memory
  unifiedStats: () => req("/unified/stats"),
  unifiedAlloc: (name: string, size: number, prefer_gpu = false) =>
    req("/unified/alloc", { method: "POST", body: JSON.stringify({ name, size, prefer_gpu }) }),

  // ACP
  acp: (method: string, params: any = {}, id = 1) =>
    req("/acp", { method: "POST", body: JSON.stringify({ id, method, params }) }),

  // Cancel demo
  cancelDemo: (kind: string) => req("/cancel/demo", { method: "POST", body: JSON.stringify({ kind }) }),
};
