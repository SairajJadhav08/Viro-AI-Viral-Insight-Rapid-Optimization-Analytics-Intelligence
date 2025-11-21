/**
 * React Query hooks for authentication
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi, SignInRequest, SignUpRequest } from '@/lib/api/auth';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api/client';

export const useSignIn = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SignInRequest) => authApi.signIn(data),
    onSuccess: (data) => {
      // Ensure token is stored before doing anything else
      if (!data || !data.access_token) {
        toast.error('Login failed: No token received from server');
        return;
      }
      
      // Store token synchronously
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', data.access_token);
        // Update API client instance
        apiClient.setToken(data.access_token);
      }
      
      // Update query cache
      if (data.user) {
        queryClient.setQueryData(['user'], data.user);
      }
      
      // Show success message
      toast.success('Signed in successfully');
      
      // Navigate after ensuring token is stored
      // Use requestAnimationFrame to ensure localStorage write is complete
      requestAnimationFrame(() => {
        navigate('/dashboard/explore', { replace: true });
      });
    },
    onError: (error: { message?: string; status?: number; detail?: string }) => {
      // Show the actual error message from backend
      let errorMessage = error.detail || error.message || 'Failed to sign in. Please check your credentials.';
      
      // Provide helpful message for network/timeout errors
      if (error.status === 0 || error.detail === 'TIMEOUT' || error.detail === 'NETWORK_ERROR') {
        errorMessage = error.message || 'Cannot connect to server. Please ensure the backend is running at http://localhost:8000';
      }
      
      toast.error(errorMessage);
      console.error('Sign in error:', error);
    },
  });
};

export const useSignUp = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: SignUpRequest) => authApi.signUp(data),
    onSuccess: (data) => {
      // Ensure token is stored before doing anything else
      if (!data || !data.access_token) {
        toast.error('Sign up failed: No token received from server');
        return;
      }
      
      // Store token synchronously
      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', data.access_token);
        // Update API client instance
        apiClient.setToken(data.access_token);
      }
      
      // Update query cache
      if (data.user) {
        queryClient.setQueryData(['user'], data.user);
      }
      
      // Show success message
      toast.success('Account created successfully');
      
      // Navigate after ensuring token is stored
      // Use requestAnimationFrame to ensure localStorage write is complete
      requestAnimationFrame(() => {
        navigate('/dashboard/explore', { replace: true });
      });
    },
    onError: (error: { message?: string; status?: number; detail?: string }) => {
      // Show the actual error message from backend
      let errorMessage = error.detail || error.message || 'Failed to create account. Please try again.';
      
      // Provide helpful message for network/timeout errors
      if (error.status === 0 || error.detail === 'TIMEOUT' || error.detail === 'NETWORK_ERROR') {
        errorMessage = error.message || 'Cannot connect to server. Please ensure the backend is running at http://localhost:8000';
      }
      
      toast.error(errorMessage);
      console.error('Sign up error:', error);
    },
  });
};

export const useSignOut = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => {
      authApi.signOut();
      return Promise.resolve();
    },
    onSuccess: () => {
      queryClient.clear();
      navigate('/login');
    },
  });
};

export const useCurrentUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: async () => {
      try {
        return await authApi.getCurrentUser();
      } catch (error: any) {
        // Handle 403/401/404 errors gracefully - return null instead of throwing
        // These are expected when user is not authenticated or endpoint doesn't exist
        if (error?.status === 403 || error?.status === 401 || error?.status === 404) {
          return null;
        }
        throw error;
      }
    },
    retry: (failureCount, error: any) => {
      // Don't retry on 403/401/404 errors (authentication issues or missing endpoint)
      if (error?.status === 403 || error?.status === 401 || error?.status === 404) {
        return false;
      }
      return failureCount < 2;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    // Don't throw errors for expected authentication failures
    // This prevents React Query from showing error toasts
    onError: () => {
      // Silently handle errors - we're using demo data as fallback
    },
  });
};

export const useUpdateProfile = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Parameters<typeof authApi.updateProfile>[0]) => authApi.updateProfile(data),
    onSuccess: (data) => {
      // Update the query cache with the new data
      queryClient.setQueryData(['user'], data);
      // Invalidate to ensure all components using this query get the update
      queryClient.invalidateQueries({ queryKey: ['user'] });
      toast.success('Profile updated successfully');
    },
    onError: (error: { message?: string; status?: number }) => {
      // Don't show error toast for 404 errors (endpoint not available - using demo mode)
      if (error?.status !== 404) {
        toast.error(error.message || 'Failed to update profile');
      }
      // Silently handle 404 - profile changes are stored locally in formData
    },
  });
};

