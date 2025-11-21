/**
 * React Query hooks for projects
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { projectsApi, CreateProjectRequest } from '@/lib/api/projects';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/lib/api/client';

export const useProjects = (page = 1, pageSize = 20) => {
  return useQuery({
    queryKey: ['projects', page, pageSize],
    queryFn: async () => {
      try {
        return await projectsApi.list(page, pageSize);
      } catch (error: any) {
        // Handle 403/401 errors gracefully - return empty data instead of throwing
        if (error?.status === 403 || error?.status === 401) {
          return {
            items: [],
            projects: [],
            total: 0,
            page: page,
            page_size: pageSize
          };
        }
        throw error;
      }
    },
    retry: (failureCount, error: any) => {
      // Don't retry on 403/401 errors (authentication issues)
      if (error?.status === 403 || error?.status === 401) {
        return false;
      }
      return failureCount < 3;
    },
  });
};

export const useProject = (id: number | null) => {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => (id ? projectsApi.get(id) : null),
    enabled: !!id,
  });
};

export const useCreateProject = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateProjectRequest) => projectsApi.create(data),
    onSuccess: (project) => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project created successfully');
      navigate(`/dashboard/result?projectId=${project.id}`);
    },
    onError: (error: { message?: string; status?: number }) => {
      // Handle authentication errors
      if (error?.status === 401 || error?.status === 403) {
        // Check if token exists in localStorage BEFORE clearing
        const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
        
        if (token) {
          // Token existed but was invalid/expired - clear it
          if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
            // Clear from API client instance
            apiClient.setToken(null);
          }
          toast.error('Your session has expired. Please sign in again.');
        } else {
          // No token was present - user not logged in
          toast.error('Please sign in to create a project');
        }
        
        // Redirect to login
        navigate('/login');
        return;
      }
      
      // Handle network errors (backend unavailable)
      if (error?.status === 0 || error?.status === 404) {
        // Backend is not available - show user-friendly message
        toast.error('Unable to connect to server. Please check if the backend is running.');
        return;
      }
      
      // Handle other errors
      toast.error(error.message || 'Failed to create project. Please try again.');
    },
  });
};

export const useDeleteProject = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast.success('Project deleted successfully');
    },
    onError: (error: any) => {
      // Handle network errors
      if (error?.status === 0 || error?.message?.includes('Network error')) {
        toast.error('Network error. Please check your connection.');
        return;
      }
      
      // Handle server errors
      if (error?.status === 500) {
        toast.error('Server error. Please try again later.');
        return;
      }
      
      // Handle not found
      if (error?.status === 404) {
        toast.error('Project not found. It may have already been deleted.');
        // Still invalidate queries to refresh the list
        queryClient.invalidateQueries({ queryKey: ['projects'] });
        return;
      }
      
      // Handle other errors
      toast.error(error?.message || error?.detail || 'Failed to delete project. Please try again.');
    },
  });
};

