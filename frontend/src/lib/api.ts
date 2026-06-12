// src/lib/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('rozgar_session');
    if (!raw) return null;
    return JSON.parse(raw).access_token || null;
  } catch {
    return null;
  }
}

export async function fetchApi(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  if (!API_URL) {
    throw new Error('NEXT_PUBLIC_API_URL is not configured. Add it to .env.local');
  }

  const token = getAuthToken();
  const isFormData = options.body instanceof FormData;

  const headers: Record<string, string> = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> || {}),
  };

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errMsg = `API ${response.status}`;
      try {
        const errBody = await response.json();
        errMsg = errBody.detail || errBody.message || errMsg;
      } catch {}
      throw new Error(errMsg);
    }

    return response.json();
  } catch (err: any) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error(
        `Cannot reach backend at ${API_URL}. Is FastAPI running? (uvicorn backend.main:app --reload)`
      );
    }
    throw err;
  }
}

// Helper to persist session from auth responses
export function saveSession(data: { access_token: string; user_id: string; role: string; name?: string }) {
  localStorage.setItem('rozgar_session', JSON.stringify(data));
}

export function getSession() {
  try {
    const raw = localStorage.getItem('rozgar_session');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function clearSession() {
  localStorage.removeItem('rozgar_session');
}
