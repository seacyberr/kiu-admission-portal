/**
 * Auth Context - Authentication state management
 * Updated for standardized API responses (Phase 4)
 */
import React, { createContext, useContext, useState, useCallback } from 'react';
import { apiPost, ApiError } from '../../../services/api';

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'applicant' | 'finalist' | 'admin';
  is_verified: boolean;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  authError: string | null;
  fieldErrors: Record<string, string> | null;
  clearErrors: () => void;
}

interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string> | null>(null);

  const clearErrors = useCallback(() => {
    setAuthError(null);
    setFieldErrors(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    clearErrors();
    try {
      // Response is now extracted directly from standardized format by apiFetch
      const data = await apiPost<{ user: User; accessToken: string; refreshToken: string }>('/v1/auth/login', { email, password });
      setUser(data.user);
      // Store user data only - auth token is in httpOnly cookie
      localStorage.setItem('kiu_user', JSON.stringify(data.user));
    } catch (error) {
      if (error instanceof ApiError) {
        setAuthError(error.message);
        setFieldErrors(error.errors || null);
      } else {
        setAuthError('Login failed. Please try again.');
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [clearErrors]);

  const logout = useCallback(async () => {
    // Call logout endpoint to clear httpOnly cookies server-side
    try {
      await apiPost('/auth/logout', {});
    } catch (e) {
      // Ignore errors - still clear local state
    }
    setUser(null);
    localStorage.removeItem('kiu_user');
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    setIsLoading(true);
    clearErrors();
    try {
      await apiPost('/v1/auth/register', data);
    } catch (error) {
      if (error instanceof ApiError) {
        setAuthError(error.message);
        setFieldErrors(error.errors || null);
      } else {
        setAuthError('Registration failed. Please try again.');
      }
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [clearErrors]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    register,
    authError,
    fieldErrors,
    clearErrors,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
