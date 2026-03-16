import { useAuth } from "../context/AuthContext";

const API_KEY = import.meta.env.VITE_CLUB_API_KEY ?? "dev-secret-key-change-in-prod";

export function useApi() {
  const { token } = useAuth();

  async function apiFetch(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      "X-Club-Key": API_KEY,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    };

    const resp = await fetch(`/api${path}`, { ...options, headers });
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: `HTTP ${resp.status}` }));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }
    return resp.json();
  }

  return { apiFetch };
}
