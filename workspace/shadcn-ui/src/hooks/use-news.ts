/**
 * React Query hooks for news
 */

import { useQuery } from '@tanstack/react-query';
import { newsApi } from '@/lib/api/news';

export const useNews = (page = 1, pageSize = 20, search?: string, topic?: string) => {
  return useQuery({
    queryKey: ['news', page, pageSize, search, topic],
    queryFn: () => newsApi.list(page, pageSize, search, topic),
  });
};

export const useNewsArticle = (id: number | null) => {
  return useQuery({
    queryKey: ['news-article', id],
    queryFn: () => (id ? newsApi.get(id) : null),
    enabled: !!id,
  });
};

