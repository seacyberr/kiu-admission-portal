/**
 * API Client with Interceptors
 * Industry-standard HTTP client with auth, error handling, and retry logic
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

interface ApiError extends Error {
  status: number;
  data?: any;
}

interface RequestConfig extends RequestInit {
  skipAuth?: boolean;
  retry?: boolean;
  maxRetries?: number;
}

class ApiClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  private async request<T>(
    endpoint: string,
    config: RequestConfig = {},
    retryCount = 0
  ): Promise<T> {
    const { skipAuth = false, retry = true, maxRetries = 3, ...fetchConfig } = config;
    
    // Build URL
    const url = `${this.baseURL}${endpoint}`;
    
    // Build headers
    const headers: Record<string, string> = {
      ...this.defaultHeaders,
      ...((fetchConfig.headers as Record<string, string>) || {}),
    };

    // Auth is handled via httpOnly cookies - credentials:include sends them automatically
    // No need to manually add Authorization header

    try {
      const response = await fetch(url, {
        ...fetchConfig,
        credentials: 'include',  // Send httpOnly cookies with every request
        headers,
      });

      // Handle 401 - Token expired
      if (response.status === 401 && !skipAuth && retryCount < maxRetries) {
        const refreshed = await this.refreshToken();
        if (refreshed) {
          return this.request(endpoint, config, retryCount + 1);
        }
        // Token refresh failed, logout user
        this.handleAuthError();
        throw new Error('Session expired');
      }

      // Handle 403 - Forbidden
      if (response.status === 403) {
        throw new Error('Access denied');
      }

      // Handle 429 - Rate limited
      if (response.status === 429) {
        if (retry && retryCount < maxRetries) {
          const delay = Math.pow(2, retryCount) * 1000; // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.request(endpoint, config, retryCount + 1);
        }
        throw new Error('Too many requests. Please try again later.');
      }

      // Handle other errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const error = new Error(
          errorData?.message || `HTTP ${response.status}: ${response.statusText}`
        ) as ApiError;
        error.status = response.status;
        error.data = errorData;
        throw error;
      }

      // Parse response
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return await response.json();
      }
      return await response.text() as unknown as T;

    } catch (error) {
      // Network errors with retry
      if (retry && retryCount < maxRetries && this.isNetworkError(error)) {
        const delay = Math.pow(2, retryCount) * 1000;
        await new Promise(resolve => setTimeout(resolve, delay));
        return this.request(endpoint, config, retryCount + 1);
      }

      throw error;
    }
  }

  private async refreshToken(): Promise<boolean> {
    try {
      // Refresh token is in httpOnly cookie - sent automatically with credentials:include
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      return response.ok;
    } catch {
      return false;
    }
  }

  private handleAuthError() {
    // Clear any local user data - auth tokens are in httpOnly cookies (cleared by backend logout)
    localStorage.removeItem('kiu_user');
    window.location.href = '/login?expired=true';
  }

  private isNetworkError(error: any): boolean {
    return error instanceof TypeError && 
      (error.message.includes('fetch') || 
       error.message.includes('network') ||
       error.message.includes('Failed to fetch'));
  }

  // HTTP methods
  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'GET' });
  }

  async post<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async patch<T>(endpoint: string, data?: any, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, {
      ...config,
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>(endpoint, { ...config, method: 'DELETE' });
  }

  // File upload
  async upload<T>(
    endpoint: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    // For file uploads, use XMLHttpRequest to track progress
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
          resolve(JSON.parse(xhr.responseText));
        } else {
          reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('Upload failed'));
      });

      xhr.open('POST', `${this.baseURL}${endpoint}`);
      // Note: XMLHttpRequest doesn't support withCredentials for FormData the same way fetch does
      // The browser will send cookies automatically for same-origin requests
      // For cross-origin, this would need additional configuration

      xhr.send(formData);
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);

// React hook for using API in components
export const useApi = () => {
  return apiClient;
};

// Pre-configured API endpoints
export const api = {
  auth: {
    login: (data: { email: string; password: string }) => 
      apiClient.post('/auth/login', data, { skipAuth: true }),
    register: (data: any) => 
      apiClient.post('/auth/register', data, { skipAuth: true }),
    logout: () => apiClient.post('/auth/logout'),
    refresh: () => apiClient.post('/auth/refresh'),
    me: () => apiClient.get('/auth/me'),
  },
  admissions: {
    apply: (data: any) => apiClient.post('/apply', data),
    getApplications: () => apiClient.get('/admissions/my-applications'),
    getApplication: (id: string) => apiClient.get(`/admissions/${id}`),
    uploadDocument: (id: string, file: File, onProgress?: (p: number) => void) => 
      apiClient.upload(`/admissions/${id}/documents`, file, onProgress),
  },
  programs: {
    getAll: () => apiClient.get('/programs'),
    getById: (id: string) => apiClient.get(`/programs/${id}`),
  },
  recommendations: {
    assess: (data: any) => apiClient.post('/recommendations/assess', data, { skipAuth: true }),
    getPrograms: (params?: string) => apiClient.get(`/recommendations/programs?${params || ''}`),
  },
  admin: {
    getApplications: (params?: string) => apiClient.get(`/admin/applications?${params || ''}`),
    getApplication: (id: string) => apiClient.get(`/admin/applications/${id}`),
    makeDecision: (id: string, data: any) => apiClient.post(`/admin/applications/${id}/decision`, data),
    scheduleInterview: (id: string, data: any) => apiClient.post(`/admin/applications/${id}/schedule-interview`, data),
  },
};
