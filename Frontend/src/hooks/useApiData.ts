import { useState, useEffect, useCallback } from 'react';
import { apiService } from '@/lib/api';

export interface UseApiDataState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

/**
 * Custom hook for fetching data from API with loading and error states
 * @param fetchFn - Async function that returns data from API
 * @param dependencies - Dependencies array to trigger refetch
 * @returns State object with data, loading, and error
 */
export function useApiData<T>(
  fetchFn: () => Promise<T>,
  dependencies: any[] = []
): UseApiDataState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchFn();
        if (isMounted) {
          setData(result);
        }
      } catch (err) {
        if (isMounted) {
          const message = err instanceof Error ? err.message : 'An error occurred';
          console.error('API Error:', message, err);
          setError(message);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      isMounted = false;
    };
  }, dependencies);

  return { data, loading, error };
}

/**
 * Hook for fetching dashboard statistics
 */
export function useDashboardStats() {
  return useApiData(
    () => apiService.getDashboardStats(),
    []
  );
}

/**
 * Hook for fetching monthly trends
 */
export function useMonthlyTrends() {
  return useApiData(
    () => apiService.getMonthlyTrends(),
    []
  );
}

/**
 * Hook for fetching churn by location
 */
export function useChurnByLocation() {
  return useApiData(
    () => apiService.getChurnByLocation(),
    []
  );
}

/**
 * Hook for fetching churn by age
 */
export function useChurnByAge() {
  return useApiData(
    () => apiService.getChurnByAge(),
    []
  );
}

/**
 * Hook for fetching churn by income
 */
export function useChurnByIncome() {
  return useApiData(
    () => apiService.getChurnByIncome(),
    []
  );
}

/**
 * Hook for fetching recent activities
 */
export function useRecentActivities() {
  return useApiData(
    () => apiService.getRecentActivities(),
    []
  );
}

/**
 * Hook for fetching customers/policy holders
 */
export function useCustomers(params?: any) {
  return useApiData(
    () => apiService.getCustomers(params),
    [params]
  );
}

/**
 * Hook for fetching claims
 */
export function useClaims(params?: any) {
  return useApiData(
    () => apiService.getClaims(params),
    [params]
  );
}

/**
 * Hook for fetching churn predictions
 */
export function useChurnPredictions(params?: any) {
  return useApiData(
    () => apiService.getPredictions(params),
    [params]
  );
}
