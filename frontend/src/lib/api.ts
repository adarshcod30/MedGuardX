const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function request(path: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('medguardx_token') : null;
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
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
    request('/api/register', { method: 'POST', body: JSON.stringify({ username, password, role, full_name }) }),

  // Upload
  upload: (file: File, patientId?: string) => {
    const formData = new FormData();
    formData.append('file', file);
    if (patientId) {
      formData.append('patient_id', patientId);
    }
    return request('/api/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Retrieve
  retrieve: (patient_id: string, role: string, purpose: string, consent: boolean) =>
    request('/api/retrieve', { method: 'POST', body: JSON.stringify({ patient_id, role, purpose, consent }) }),

  // Preview
  preview: (text: string, role: string, purpose: string, consent: boolean) =>
    request('/api/preview', { method: 'POST', body: JSON.stringify({ text, role, purpose, consent }) }),

  // Stats & Audit
  stats: () => request('/api/stats'),
  audit: (limit = 50, offset = 0) => request(`/api/audit?limit=${limit}&offset=${offset}`),
  patients: () => request('/api/patients'),
};
