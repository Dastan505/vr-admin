import type { Game, Resource, Session, SessionCreate, SessionUpdate, UserInfo } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

let authToken = localStorage.getItem("vr_admin_token") || "";

export function setToken(token: string) {
  authToken = token;
  if (token) {
    localStorage.setItem("vr_admin_token", token);
  } else {
    localStorage.removeItem("vr_admin_token");
  }
}

async function request<T>(path: string, options: RequestInit = {}, useAuth = true): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (useAuth && authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

export async function login(email: string, password: string): Promise<{ access_token: string; user: UserInfo }> {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password })
  }, false);
}

export async function getGames(): Promise<Game[]> {
  return request("/games?active_only=true");
}

export async function getResources(): Promise<Resource[]> {
  return request("/resources");
}

export async function getCalendarDay(date: string): Promise<Session[]> {
  return request(`/calendar/day?date=${date}`);
}

export async function createSession(payload: SessionCreate): Promise<Session> {
  return request("/sessions", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function updateSession(id: number, payload: SessionUpdate): Promise<Session> {
  return request(`/sessions/${id}`, {
    method: "PUT",
    body: JSON.stringify(payload)
  });
}

export async function cancelSession(id: number, reason: string): Promise<Session> {
  return request(`/sessions/${id}/cancel`, {
    method: "POST",
    body: JSON.stringify({ reason })
  });
}

export async function completeSession(id: number): Promise<Session> {
  return request(`/sessions/${id}/complete`, { method: "POST" });
}

export async function deleteSession(id: number, reason: string): Promise<{ status: string }> {
  return request(`/sessions/${id}`, {
    method: "DELETE",
    body: JSON.stringify({ reason })
  });
}
