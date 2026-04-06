/**
 * Base API client for KIU Portal.
 * Uses httpOnly cookies for authentication (credentials: 'include').
 */

const API_BASE = import.meta.env.VITE_API_URL || '/api';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

let isRefreshing = false;
let refreshPromise: Promise<void> | null = null;

async function handleTokenRefresh() {
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const refreshResponse = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (!refreshResponse.ok) {
        throw new Error('Refresh failed');
      }
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = 'GET', body, headers = {} } = options;

  if (body && method !== 'GET') {
    headers['Content-Type'] = 'application/json';
  }

  let response = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers,
    credentials: 'include', // Send httpOnly cookies with every request
    body: body ? JSON.stringify(body) : undefined,
  });

  // If unauthorized, try to refresh token once and retry the original request
  if (response.status === 401 && endpoint !== '/auth/refresh') {
    try {
      await handleTokenRefresh();
      
      // Retry original request with fresh token
      response = await fetch(`${API_BASE}${endpoint}`, {
        method,
        headers,
        credentials: 'include',
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch (refreshError) {
      // Refresh failed - clear auth state and redirect to login
      window.location.href = '/login';
      throw new Error('Session expired');
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `API error: ${response.status}`);
  }

  return response.json();
}

export function apiGet<T>(endpoint: string): Promise<T> {
  return apiFetch<T>(endpoint);
}

export function apiPost<T>(endpoint: string, body: unknown): Promise<T> {
  return apiFetch<T>(endpoint, { method: 'POST', body });
}

export function apiPatch<T>(endpoint: string, body: unknown): Promise<T> {
  return apiFetch<T>(endpoint, { method: 'PATCH', body });
}

export function apiDelete<T>(endpoint: string): Promise<T> {
  return apiFetch<T>(endpoint, { method: 'DELETE' });
}