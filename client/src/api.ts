const BASE = "";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (resp.status === 401) {
    window.location.href = "/auth/google";
    throw new Error("Unauthorized");
  }
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`${resp.status}: ${text}`);
  }
  return resp.json();
}

// Auth
export const getMe = () => request<{ authenticated: boolean; user?: { email: string; name: string; picture: string } }>("/auth/me");
export const logout = () => request("/auth/logout", { method: "POST" });

// Status
export const getStatus = () => request<import("./types").StatusData>("/api/status");

// SBOM
export const getSbom = (params?: string) => request<{ components: import("./types").Component[]; total: number }>(`/api/sbom${params ? `?${params}` : ""}`);
export const getSbomDiff = () => request<{ diff: unknown; snapshot_date?: string }>("/api/sbom/diff");

// Risks
export const getRisks = (params?: string) => request<{ risks: import("./types").RiskItem[]; total: number }>(`/api/risks${params ? `?${params}` : ""}`);
export const updateRisk = (id: number, data: Record<string, string>) =>
  request<import("./types").RiskItem>(`/api/risks/${id}`, { method: "PATCH", body: JSON.stringify(data) });

// Actions
export const getActions = (params?: string) => request<{ actions: import("./types").ActionItem[]; total: number }>(`/api/actions${params ? `?${params}` : ""}`);
export const updateAction = (id: number, data: Record<string, string>) =>
  request<import("./types").ActionItem>(`/api/actions/${id}`, { method: "PATCH", body: JSON.stringify(data) });

// Feed
export const getFeed = (params?: string) => request<{ entries: import("./types").FeedEntry[]; total: number }>(`/api/feed${params ? `?${params}` : ""}`);

// Brief
export const getBrief = () => request<Record<string, unknown>>("/api/brief");

// Modules
export const getModules = () => request<{ modules: import("./types").ModuleRun[] }>("/api/modules");
export const refreshAll = () => request<{ ran: number; success: number; failed: number; results: unknown[] }>("/api/refresh", { method: "POST" });
export const refreshModule = (name: string) => request(`/api/refresh/${name}`, { method: "POST" });

// History
export const getHistory = (params?: string) => request<{ events: unknown[]; total: number }>(`/api/history${params ? `?${params}` : ""}`);

// Monitoring
export const getMonitoring = () => request<import("./types").MonitoringData>("/api/monitoring");

// Health
export const getHealth = () => request<{ status: string; database: string; db_latency_ms: number; uptime_seconds: number; version: string }>("/api/health");
