const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const TOKEN_KEY = 'medguardx_token';
const ROLE_KEY = 'medguardx_role';
const USER_KEY = 'medguardx_user';

export function getToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;
}

export function getRole(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(ROLE_KEY) : null;
}

export function getUsername(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(USER_KEY) : null;
}

export function setSession(token: string, role: string, username: string) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(ROLE_KEY, role);
  localStorage.setItem(USER_KEY, username);
}

export function clearSession() {
  [TOKEN_KEY, ROLE_KEY, USER_KEY].forEach((k) => localStorage.removeItem(k));
}

async function request(path: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // A rejected token means the session is stale -- clear it so the UI can prompt
  // a fresh login instead of silently retrying.
  if (res.status === 401) {
    clearSession();
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export const api = {
  // Auth
  login: (username: string, password: string) =>
    request('/api/login', { method: 'POST', body: JSON.stringify({ username, password }) }),
  register: (username: string, password: string, role: string, full_name: string) =>
    request('/api/register', {
      method: 'POST',
      body: JSON.stringify({ username, password, role, full_name }),
    }),

  // Upload (auth required; patient owner derived from the token server-side)
  upload: (file: File, patientId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (patientId) formData.append('patient_id', patientId);
    return request('/api/upload', { method: 'POST', body: formData });
  },

  // Retrieve -- NOTE: no `role`. The server derives it from the auth token.
  retrieve: (patient_id: string, purpose: string, consent: boolean) =>
    request('/api/retrieve', {
      method: 'POST',
      body: JSON.stringify({ patient_id, purpose, consent }),
    }),

  // Preview -- likewise role-free.
  preview: (text: string, purpose: string, consent: boolean) =>
    request('/api/preview', { method: 'POST', body: JSON.stringify({ text, purpose, consent }) }),

  // Stats & Audit
  stats: () => request('/api/stats'),
  audit: (limit = 50, offset = 0) => request(`/api/audit?limit=${limit}&offset=${offset}`),
};
