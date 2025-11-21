import { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, BookmarkCheck, Share2, ExternalLink, Trash2, AlertCircle } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import type { NewsArticle } from '@/lib/api/news';

// Helper functions for managing saved articles
const getSavedArticles = (): NewsArticle[] => {
  if (typeof window === 'undefined') return [];
  const saved = localStorage.getItem('saved_articles');
  return saved ? JSON.parse(saved) : [];
};

const removeSavedArticle = (articleId: number): void => {
  if (typeof window === 'undefined') return;
  const saved = getSavedArticles();
  const filtered = saved.filter(a => a.id !== articleId);
  localStorage.setItem('saved_articles', JSON.stringify(filtered));
};

export default function SavedArticles() {
  const [searchQuery, setSearchQuery] = useState('');
  const [topicFilter, setTopicFilter] = useState('all');
  const [savedArticles, setSavedArticles] = useState<NewsArticle[]>([]);

  // Load saved articles on mount and when they change
  useEffect(() => {
    const loadSavedArticles = () => {
      const saved = getSavedArticles();
      setSavedArticles(saved);
    };
    loadSavedArticles();
    
    // Listen for storage changes (in case articles are saved from other tabs)
    const handleStorageChange = () => {
      loadSavedArticles();
    };
    window.addEventListener('storage', handleStorageChange);
    
    // Also check periodically (for same-tab updates)
    const interval = setInterval(loadSavedArticles, 1000);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  // Filter saved articles
  const filteredArticles = useMemo(() => {
    let filtered = savedArticles;
    
    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(article => 
        article.title.toLowerCase().includes(query) ||
        article.summary?.toLowerCase().includes(query) ||
        article.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    }
    
    // Apply topic filter
    if (topicFilter !== 'all') {
      filtered = filtered.filter(article => 
        article.tags?.some(tag => tag.toLowerCase() === topicFilter.toLowerCase())
      );
    }
    
    // Sort by saved date (most recent first)
    return filtered.sort((a, b) => {
      const dateA = (a as any).saved_at || a.created_at || '';
      const dateB = (b as any).saved_at || b.created_at || '';
      return dateB.localeCompare(dateA);
    });
  }, [savedArticles, searchQuery, topicFilter]);

  const getCredibilityColor = (credibility: string) => {
    switch (credibility) {
      case 'Peer-reviewed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'Preprint':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Government Notice':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const handleRemove = (articleId: number) => {
    removeSavedArticle(articleId);
    setSavedArticles(getSavedArticles());
    toast.success('Article removed from saved');
  };

  const handleClearAll = () => {
    if (window.confirm('Are you sure you want to remove all saved articles?')) {
      localStorage.removeItem('saved_articles');
      setSavedArticles([]);
      toast.success('All saved articles removed');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Saved Articles</h1>
          <p className="text-[#4A6A7A]">Your bookmarked research articles and publications</p>
        </div>
        {savedArticles.length > 0 && (
          <Button variant="outline" onClick={handleClearAll}>
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        )}
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#4A6A7A]" />
              <Input
                placeholder="Search saved articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={topicFilter} onValueChange={setTopicFilter}>
              <SelectTrigger className="w-full md:w-[200px]">
                <SelectValue placeholder="Filter by topic" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Topics</SelectItem>
                <SelectItem value="genomics">Genomics</SelectItem>
                <SelectItem value="antiviral">Antiviral Discovery</SelectItem>
                <SelectItem value="outbreaks">Outbreaks</SelectItem>
                <SelectItem value="structural">Structural Biology</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      {savedArticles.length > 0 && (
        <div className="flex items-center gap-4 text-sm text-[#4A6A7A]">
          <span>Total saved: <strong className="text-[#0B2336]">{savedArticles.length}</strong></span>
          {filteredArticles.length !== savedArticles.length && (
            <span>Showing: <strong className="text-[#0B2336]">{filteredArticles.length}</strong></span>
          )}
        </div>
      )}

      {/* Saved Articles List */}
      {filteredArticles.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredArticles.map((article) => (
            <Card key={article.id} className="hover:shadow-lg transition-shadow group">
              <CardHeader>
                <div className="flex items-start justify-between gap-2 mb-2">
                  {article.credibility && (
                    <Badge className={getCredibilityColor(article.credibility)} variant="outline">
                      {article.credibility}
                    </Badge>
                  )}
                  <div className="flex items-center gap-2">
                    {article.publish_date && (
                      <span className="text-xs text-[#4A6A7A]">{article.publish_date}</span>
                    )}
                    <Button
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                      onClick={() => handleRemove(article.id)}
                      title="Remove from saved"
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
                <CardTitle className="text-lg group-hover:text-[#1E88E5] transition-colors">
                  {article.title}
                </CardTitle>
                {article.summary && (
                  <CardDescription className="text-sm">{article.summary}</CardDescription>
                )}
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {article.tags && article.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {article.tags.map((tag, tagIndex) => (
                        <Badge key={tagIndex} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                  <div className="flex items-center justify-between text-sm">
                    {article.source && (
                      <span className="text-[#4A6A7A]">{article.source}</span>
                    )}
                    {article.relevance && (
                      <span className="text-[#0B4F8C] font-medium">Relevance: {article.relevance}%</span>
                    )}
                  </div>
                  <div className="flex gap-2 pt-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="flex-1"
                      onClick={async () => {
                        const shareData = {
                          title: article.title,
                          text: article.summary || '',
                          url: article.link || window.location.href,
                        };
                        try {
                          if (navigator.share) {
                            await navigator.share(shareData);
                            toast.success('Shared successfully!');
                          } else {
                            await navigator.clipboard.writeText(article.link || window.location.href);
                            toast.success('Link copied to clipboard!');
                          }
                        } catch (error: any) {
                          if (error.name !== 'AbortError') {
                            await navigator.clipboard.writeText(article.link || window.location.href);
                            toast.success('Link copied to clipboard!');
                          }
                        }
                      }}
                    >
                      <Share2 className="h-4 w-4 mr-1" />
                      Share
                    </Button>
                    {article.link && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        className="flex-1"
                        onClick={() => window.open(article.link, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4 mr-1" />
                        Read
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-12 pb-12">
            <div className="flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-yellow-100 flex items-center justify-center">
                <BookmarkCheck className="h-8 w-8 text-yellow-600" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-semibold text-[#0B2336]">
                  {savedArticles.length === 0 
                    ? 'No saved articles yet' 
                    : 'No articles match your search'}
                </h3>
                <p className="text-[#4A6A7A] max-w-md">
                  {savedArticles.length === 0
                    ? 'Start exploring articles and save the ones you find interesting!'
                    : 'Try adjusting your search or filter criteria.'}
                </p>
              </div>
              {savedArticles.length === 0 && (
                <Button
                  onClick={() => window.location.href = '/dashboard/explore'}
                  className="bg-[#0B4F8C] hover:bg-[#0A3D6F] text-white"
                >
                  Explore Articles
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

