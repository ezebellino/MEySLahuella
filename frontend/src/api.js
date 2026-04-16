const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function request(path, options = {}) {
  const {
    timeoutMs = 12000,
    retries = 0,
    retryDelayMs = 350,
    ...fetchOptions
  } = options;

  let attempt = 0;
  let lastError = null;
  const maxAttempts = 1 + Math.max(0, retries);

  while (attempt < maxAttempts) {
    attempt += 1;
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const res = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...fetchOptions,
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        const err = new Error(body.detail || `Error ${res.status}`);
        err.status = res.status;
        throw err;
      }

      const payload = await res.json();
      if (payload && typeof payload === "object" && !Array.isArray(payload)) {
        payload._meta = { attempts: attempt, retried: attempt > 1 };
      }
      return payload;
    } catch (error) {
      clearTimeout(timeoutId);
      const isAbort = error?.name === "AbortError";
      const status = error?.status ?? 0;
      const canRetry =
        attempt < maxAttempts && (isAbort || status >= 500 || status === 0 || !status);
      if (!canRetry) {
        lastError = isAbort ? new Error("Timeout de red. Reintentá en unos segundos.") : error;
        break;
      }
      const backoff = retryDelayMs * Math.pow(2, attempt - 1);
      await sleep(backoff);
      lastError = error;
    }
  }

  throw lastError || new Error("Error de red");
}

export const api = {
  health: () => request("/health", { timeoutMs: 5000, retries: 1 }),
  systemInfo: () => request("/system/info", { timeoutMs: 7000, retries: 1 }),
  antenna: () => request("/antenna", { timeoutMs: 7000, retries: 1 }),
  updatePotencia: (potencia) =>
    request("/antenna/potencia", {
      method: "PUT",
      body: JSON.stringify({ potencia }),
      timeoutMs: 10000,
      retries: 1,
    }),
  tags: () => request("/tags", { timeoutMs: 8000, retries: 1 }),
  moveFiles: (source_path, destination_path) =>
    request("/files/move", {
      method: "POST",
      body: JSON.stringify({ source_path, destination_path }),
      timeoutMs: 18000,
      retries: 1,
    }),
  hosts: () => request("/hosts", { timeoutMs: 9000, retries: 1 }),
  createHost: (payload) =>
    request("/hosts", { method: "POST", body: JSON.stringify(payload), timeoutMs: 10000, retries: 1 }),
  updateHost: (id, payload) =>
    request(`/hosts/${id}`, { method: "PUT", body: JSON.stringify(payload), timeoutMs: 10000, retries: 1 }),
  deleteHost: (id) => request(`/hosts/${id}`, { method: "DELETE", timeoutMs: 10000, retries: 1 }),
  getHostTopology: (id) => request(`/hosts/${id}/topology`, { timeoutMs: 10000, retries: 1 }),
  updateHostTopology: (id, payload) =>
    request(`/hosts/${id}/topology`, { method: "PUT", body: JSON.stringify(payload), timeoutMs: 12000, retries: 1 }),
  discoverHosts: (subnet, port = 445) =>
    request("/hosts/discover", {
      method: "POST",
      body: JSON.stringify({ subnet, port }),
      timeoutMs: 60000,
      retries: 0,
    }),
  listHostFiles: (id, path) =>
    request(`/hosts/${id}/files/list`, {
      method: "POST",
      body: JSON.stringify({ path }),
      timeoutMs: 15000,
      retries: 1,
    }),
  restartTerminal: (id) => request(`/hosts/${id}/terminal/restart`, { method: "POST", timeoutMs: 20000, retries: 1 }),
  runCommand: (id, command) =>
    request(`/hosts/${id}/command`, {
      method: "POST",
      body: JSON.stringify({ command }),
      timeoutMs: 20000,
      retries: 1,
    }),
  testCredentials: (id, candidates) =>
    request(`/hosts/${id}/credentials/test`, {
      method: "POST",
      body: JSON.stringify({ candidates }),
      timeoutMs: 18000,
      retries: 1,
    }),
  quickCheckHost: (id, include_auth = true) =>
    request(`/hosts/${id}/quick-check`, {
      method: "POST",
      body: JSON.stringify({ include_auth }),
      timeoutMs: 12000,
      retries: 2,
    }),
  rotateCredentials: (id, username, password, verify = true, rollback_on_fail = true) =>
    request(`/hosts/${id}/credentials/rotate`, {
      method: "POST",
      body: JSON.stringify({ username, password, verify, rollback_on_fail }),
      timeoutMs: 25000,
      retries: 1,
    }),
  rotationHistory: (host_id = "", limit = 100) => {
    const q = new URLSearchParams();
    if (host_id) q.set("host_id", host_id);
    q.set("limit", String(limit));
    return request(`/credentials/rotation-history?${q.toString()}`, { timeoutMs: 10000, retries: 1 });
  },
  auditEvents: ({
    host_id = "",
    event_type = "",
    status = "",
    date_from = "",
    date_to = "",
    limit = 200,
  } = {}) => {
    const q = new URLSearchParams();
    if (host_id) q.set("host_id", host_id);
    if (event_type) q.set("event_type", event_type);
    if (status) q.set("status", status);
    if (date_from) q.set("date_from", date_from);
    if (date_to) q.set("date_to", date_to);
    q.set("limit", String(limit));
    return request(`/audit/events?${q.toString()}`, { timeoutMs: 12000, retries: 1 });
  },
  uploadText: (id, remote_path, content) =>
    request(`/hosts/${id}/transfer/upload-text`, {
      method: "POST",
      body: JSON.stringify({ remote_path, content }),
      timeoutMs: 22000,
      retries: 1,
    }),
  downloadText: (id, remote_path) =>
    request(`/hosts/${id}/transfer/download-text`, {
      method: "POST",
      body: JSON.stringify({ remote_path }),
      timeoutMs: 22000,
      retries: 1,
    })
};
