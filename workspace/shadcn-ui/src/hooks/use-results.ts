/**
 * React Query hooks for results
 */

import { useQuery } from '@tanstack/react-query';
import { resultsApi } from '@/lib/api/results';

export const useProjectResults = (projectId: number | null) => {
  return useQuery({
    queryKey: ['project-results', projectId],
    queryFn: async () => {
      if (!projectId) return null;
      try {
        return await resultsApi.getProjectResults(projectId);
      } catch (error: any) {
        // If 404 with PROCESSING, return null (still processing)
        if (error?.status === 404 && error?.detail === 'PROCESSING') {
          return null;
        }
        throw error;
      }
    },
    enabled: !!projectId,
    retry: (failureCount, error: any) => {
      // Don't retry if it's a processing state (404 with PROCESSING)
      if (error?.status === 404 && error?.detail === 'PROCESSING') {
        return false;
      }
      // Retry other errors up to 3 times
      return failureCount < 3;
    },
    refetchInterval: (query) => {
      // If results are null (processing), refetch every 2 seconds for faster updates
      if (query.state.data === null) {
        return 2000;
      }
      // Otherwise, don't auto-refetch
      return false;
    },
  });
};

export const useMutations = (projectId: number | null) => {
  return useQuery({
    queryKey: ['mutations', projectId],
    queryFn: () => (projectId ? resultsApi.getMutations(projectId) : null),
    enabled: !!projectId,
  });
};

export const useDrugs = (projectId: number | null) => {
  return useQuery({
    queryKey: ['drugs', projectId],
    queryFn: () => (projectId ? resultsApi.getDrugs(projectId) : null),
    enabled: !!projectId,
  });
};

export const useModifications = (projectId: number | null) => {
  return useQuery({
    queryKey: ['modifications', projectId],
    queryFn: () => (projectId ? resultsApi.getModifications(projectId) : null),
    enabled: !!projectId,
  });
};

