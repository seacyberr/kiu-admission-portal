/**
 * Base API client for KIU Portal.
 * Uses httpOnly cookies for authentication (credentials: 'include').
 * Updated for standardized API responses (Phase 4)
 */

import type { ApiResponse } from '../types/api';

// In development: use '/api' to go through Vite proxy (avoids CORS)
// In production: use full API URL if provided
const API_BASE = import.meta.env.DEV ? '/api' : (import.meta.env.VITE_API_URL || '/api');

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

// Maximum retry attempts for network/rate limit errors
const MAX_RETRIES = 3;

// Helper to check if error is a network error
function isNetworkError(error: any): boolean {
  return error instanceof TypeError && 
    (error.message.includes('fetch') || 
     error.message.includes('network') ||
     error.message.includes('Failed to fetch'));
}

// Helper to delay with exponential backoff
function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function executeRequest<T>(
  endpoint: string,
  options: RequestOptions,
  retryCount = 0
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

  let response: Response;
  
  try {
    response = await fetch(`${API_BASE}${endpoint}${cacheBuster}`, {
      method,
      headers,
      credentials: 'include',
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (error) {
    // Network error with retry
    if (isNetworkError(error) && retryCount < MAX_RETRIES) {
      await delay(Math.pow(2, retryCount) * 1000);
      return executeRequest(endpoint, options, retryCount + 1);
    }
    throw error;
  }

  // Handle 429 - Rate limited with exponential backoff
  if (response.status === 429 && retryCount < MAX_RETRIES) {
    await delay(Math.pow(2, retryCount) * 1000);
    return executeRequest(endpoint, options, retryCount + 1);
  }

  // If unauthorized, try to refresh token once and retry the original request
  if (response.status === 401 && endpoint !== '/auth/refresh') {
    try {
      await handleTokenRefresh();
      
      // Retry original request with fresh token
      return executeRequest(endpoint, options, 0);
    } catch (refreshError) {
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

export async function apiFetch<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  return executeRequest<T>(endpoint, options, 0);
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

// File upload with progress tracking
export function apiUpload<T>(
  endpoint: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<T> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && onProgress) {
        const progress = (event.loaded / event.total) * 100;
        onProgress(progress);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch {
          resolve(xhr.responseText as unknown as T);
        }
      } else {
        reject(new Error(`Upload failed: HTTP ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed: Network error'));
    });

    xhr.open('POST', `${API_BASE}${endpoint}`);
    // Cookies are sent automatically for same-origin requests
    
    const formData = new FormData();
    formData.append('file', file);
    xhr.send(formData);
  });
}

// Export api object for backward compatibility
export const api = {
  get: apiGet,
  post: apiPost,
  patch: apiPatch,
  delete: apiDelete,
  fetch: apiFetch,
  upload: apiUpload,
};