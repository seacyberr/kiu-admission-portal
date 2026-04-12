/**
 * useApi Hook - Example of using standardized API responses
 * 
 * This hook demonstrates how to work with the new standardized API format
 * that was implemented in Phase 3 (backend) and Phase 4 (frontend).
 */

import { useState, useCallback } from 'react';
import { ApiError } from '../services/api';

interface UseApiState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
  fieldErrors: Record<string, string> | null;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: unknown[]) => Promise<T | null>;
  clearError: () => void;
}

/**
 * Generic hook for API calls with standardized error handling
 * 
 * @example
 * const { data, isLoading, error, fieldErrors, execute } = useApi<User[]>(
 *   () => apiGet('/v1/users')
 * );
 * 
 * // In component:
 * useEffect(() => {
 *   execute();
 * }, [execute]);
 * 
 * // Display field errors:
 * {fieldErrors?.email && <span className="error">{fieldErrors.email}</span>}
 */
export function useApi<T>(apiFunction: (...args: unknown[]) => Promise<T>): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    isLoading: false,
    error: null,
    fieldErrors: null,
  });

  const execute = useCallback(async (...args: unknown[]) => {
    setState(prev => ({ ...prev, isLoading: true, error: null, fieldErrors: null }));
    
    try {
      const data = await apiFunction(...args);
      setState({ data, isLoading: false, error: null, fieldErrors: null });
      return data;
    } catch (error) {
      let errorMessage = 'An unexpected error occurred';
      let fieldErrors: Record<string, string> | null = null;
      
      if (error instanceof ApiError) {
        errorMessage = error.message;
        fieldErrors = error.errors || null;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      setState({ data: null, isLoading: false, error: errorMessage, fieldErrors });
      return null;
    }
  }, [apiFunction]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null, fieldErrors: null }));
  }, []);

  return { ...state, execute, clearError };
}

/**
 * Hook specifically for paginated data
 * 
 * @example
 * const { items, total, page, setPage, isLoading, error } = usePaginatedApi<User>(
 *   (page, perPage) => apiGet(`/v1/users?page=${page}&perPage=${perPage}`)
 * );
 */
export function usePaginatedApi<T>(
  apiFunction: (page: number, perPage: number) => Promise<{ items: T[]; total: number }>
) {
  const [items, setItems] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [perPage] = useState(20);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPage = useCallback(async (targetPage: number) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiFunction(targetPage, perPage);
      setItems(response.items);
      setTotal(response.total);
      setPage(targetPage);
    } catch (error) {
      if (error instanceof ApiError) {
        setError(error.message);
      } else {
        setError('Failed to load data');
      }
    } finally {
      setIsLoading(false);
    }
  }, [apiFunction, perPage]);

  return {
    items,
    total,
    page,
    perPage,
    isLoading,
    error,
    setPage: fetchPage,
    refetch: () => fetchPage(page),
  };
}

/**
 * Hook for mutations (POST, PATCH, DELETE) with success/error handling
 * 
 * @example
 * const { mutate, isLoading, error, fieldErrors, isSuccess } = useApiMutation(
 *   (data) => apiPost('/v1/applications', data)
 * );
 * 
 * // In form submit:
 * const result = await mutate(formData);
 * if (result) {
 *   // Success - show success message or redirect
 * }
 */
export function useApiMutation<T, Args extends unknown[]>(
  apiFunction: (...args: Args) => Promise<T>
) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string> | null>(null);
  const [isSuccess, setIsSuccess] = useState(false);

  const mutate = useCallback(async (...args: Args) => {
    setIsLoading(true);
    setError(null);
    setFieldErrors(null);
    setIsSuccess(false);
    
    try {
      const result = await apiFunction(...args);
      setIsSuccess(true);
      return result;
    } catch (error) {
      if (error instanceof ApiError) {
        setError(error.message);
        setFieldErrors(error.errors || null);
      } else {
        setError('An unexpected error occurred');
      }
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [apiFunction]);

  const reset = useCallback(() => {
    setIsLoading(false);
    setError(null);
    setFieldErrors(null);
    setIsSuccess(false);
  }, []);

  return {
    mutate,
    isLoading,
    error,
    fieldErrors,
    isSuccess,
    reset,
  };
}
