/**
 * Base API client for KIU Portal.
 * Uses httpOnly cookies for authentication (credentials: 'include').
 * Updated for standardized API responses (Phase 4)
 */

import type { ApiResponse } from '../types/api';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

/**
 * Custom API Error class with field-level errors support
 */
export class ApiError extends Error {
  status: number;
  errors?: Record<string, string>;
  
  constructor(message: string, status: number, errors?: Record<string, string>) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.errors = errors;
  }
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

  // Add cache-busting headers to prevent browser caching
  headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0';
  headers['Pragma'] = 'no-cache';
  headers['Expires'] = '0';
  // Add timestamp to bust cache for GET requests
  const cacheBuster = method === 'GET' ? `?_t=${Date.now()}` : '';

  let response = await fetch(`${API_BASE}${endpoint}${cacheBuster}`, {
    method,
    headers,
    credentials: 'include', // Send httpOnly cookies with every request
    body: body ? JSON.stringify(body) : undefined,
  });

  // If unauthorized, try to refresh token once and retry the original request
  if (response.status === 401 && endpoint !== '/auth/refresh') {
    try {
      await handleTokenRefresh();
      
      // Retry original request with fresh token (also add cache-busting)
      const retryCacheBuster = method === 'GET' ? `?_t=${Date.now()}` : '';
      response = await fetch(`${API_BASE}${endpoint}${retryCacheBuster}`, {
        method,
        headers,
        credentials: 'include',
        body: body ? JSON.stringify(body) : undefined,
      });
    } catch (refreshError) {
      // Refresh failed - clear auth state
      // Note: SPA navigation should be handled by the component using this API
      localStorage.removeItem('kiu_user');
      throw new Error('Session expired');
    }
  }

  // Parse response as standardized format
  const responseData: ApiResponse<unknown> = await response.json().catch(() => ({
    status: 'error',
    data: null,
    message: `Invalid JSON response from server (status ${response.status})`
  }));
  
  // Handle non-success status codes or fail/error status
  if (!response.ok || responseData.status === 'fail' || responseData.status === 'error') {
    const message = responseData.message || `API error: ${response.status}`;
    const errors = responseData.errors;
    throw new ApiError(message, response.status, errors);
  }
  
  // Return the data from standardized response
  return responseData.data as T;
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

// Export api object for backward compatibility
export const api = {
  get: apiGet,
  post: apiPost,
  patch: apiPatch,
  delete: apiDelete,
  fetch: apiFetch,
};