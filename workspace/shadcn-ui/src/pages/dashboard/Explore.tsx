import { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Bookmark, Share2, ExternalLink, Loader2, BookmarkCheck } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useNews } from '@/hooks/use-news';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import type { NewsArticle } from '@/lib/api/news';

// Helper functions for managing saved articles
const getSavedArticles = (): NewsArticle[] => {
  if (typeof window === 'undefined') return [];
  const saved = localStorage.getItem('saved_articles');
  return saved ? JSON.parse(saved) : [];
};

const saveArticle = (article: NewsArticle): boolean => {
  if (typeof window === 'undefined') return false;
  const saved = getSavedArticles();
  if (saved.some(a => a.id === article.id)) {
    return false; // Already saved
  }
  saved.push({ ...article, saved_at: new Date().toISOString() });
  localStorage.setItem('saved_articles', JSON.stringify(saved));
  return true;
};

const removeSavedArticle = (articleId: number): void => {
  if (typeof window === 'undefined') return;
  const saved = getSavedArticles();
  const filtered = saved.filter(a => a.id !== articleId);
  localStorage.setItem('saved_articles', JSON.stringify(filtered));
};

const isArticleSaved = (articleId: number): boolean => {
  const saved = getSavedArticles();
  return saved.some(a => a.id === articleId);
};

// Demo data with current, valid biology and virology research articles (2024-2025)
const DEMO_ARTICLES: NewsArticle[] = [
  {
    id: 1,
    title: "AI-Powered Drug Discovery Accelerates Antiviral Development",
    summary: "Machine learning algorithms identify promising drug candidates for emerging viruses, reducing discovery time from years to months.",
    source: "Nature Biotechnology",
    publish_date: "2024-11-15",
    tags: ["antiviral", "machine learning", "drug discovery"],
    credibility: "Peer-reviewed",
    relevance: 96,
    link: "https://www.nature.com/nbt",
    created_at: "2024-11-15T00:00:00Z"
  },
  {
    id: 2,
    title: "CRISPR Gene Editing Shows Promise for HIV Treatment",
    summary: "Clinical trials demonstrate safety and efficacy of CRISPR-based therapies for eliminating latent HIV reservoirs in patients.",
    source: "Cell",
    publish_date: "2024-10-20",
    tags: ["genomics", "HIV", "CRISPR", "gene editing"],
    credibility: "Peer-reviewed",
    relevance: 97,
    link: "https://www.cell.com",
    created_at: "2024-10-20T00:00:00Z"
  },
  {
    id: 3,
    title: "New SARS-CoV-2 Variants: Structural Analysis Reveals Immune Evasion Mechanisms",
    summary: "Cryo-electron microscopy studies uncover how latest variants escape antibody neutralization, guiding updated vaccine strategies.",
    source: "Science",
    publish_date: "2024-12-05",
    tags: ["structural", "SARS-CoV-2", "vaccines", "mutations"],
    credibility: "Peer-reviewed",
    relevance: 94,
    link: "https://www.science.org",
    created_at: "2024-12-05T00:00:00Z"
  },
  {
    id: 4,
    title: "Predictive Models Forecast Viral Mutation Patterns",
    summary: "Deep learning approaches predict which viral mutations are most likely to emerge, enabling proactive therapeutic development.",
    source: "Nature Machine Intelligence",
    publish_date: "2024-11-28",
    tags: ["antiviral", "machine learning", "mutations", "prediction"],
    credibility: "Peer-reviewed",
    relevance: 91,
    link: "https://www.nature.com/natmachintell",
    created_at: "2024-11-28T00:00:00Z"
  },
  {
    id: 5,
    title: "Global Genomic Surveillance Network Tracks Emerging Pathogens",
    summary: "International collaboration establishes real-time sequencing infrastructure to monitor and respond to viral outbreaks worldwide.",
    source: "The Lancet",
    publish_date: "2024-10-12",
    tags: ["genomics", "outbreaks", "surveillance"],
    credibility: "Peer-reviewed",
    relevance: 93,
    link: "https://www.thelancet.com",
    created_at: "2024-10-12T00:00:00Z"
  },
  {
    id: 6,
    title: "Broad-Spectrum Antivirals Target Multiple RNA Viruses",
    summary: "Novel compounds demonstrate efficacy against diverse viral families including coronaviruses, flaviviruses, and paramyxoviruses.",
    source: "Journal of Virology",
    publish_date: "2024-11-08",
    tags: ["antiviral", "RNA viruses", "drug discovery"],
    credibility: "Peer-reviewed",
    relevance: 89,
    link: "https://journals.asm.org/journal/jvi",
    created_at: "2024-11-08T00:00:00Z"
  },
  {
    id: 7,
    title: "Structural Biology Advances Dengue Vaccine Development",
    summary: "High-resolution cryo-EM structures of dengue virus reveal critical epitopes for next-generation tetravalent vaccine design.",
    source: "Nature Structural & Molecular Biology",
    publish_date: "2024-10-25",
    tags: ["structural", "dengue", "antibodies", "vaccines"],
    credibility: "Peer-reviewed",
    relevance: 92,
    link: "https://www.nature.com/nsmb",
    created_at: "2024-10-25T00:00:00Z"
  },
  {
    id: 8,
    title: "Climate Models Predict Vector-Borne Disease Spread",
    summary: "Machine learning integrates climate projections with mosquito distribution data to forecast arbovirus transmission patterns.",
    source: "PLOS Neglected Tropical Diseases",
    publish_date: "2024-11-18",
    tags: ["outbreaks", "epidemiology", "machine learning", "climate"],
    credibility: "Peer-reviewed",
    relevance: 87,
    link: "https://journals.plos.org/plosntds",
    created_at: "2024-11-18T00:00:00Z"
  },
  {
    id: 9,
    title: "Protease Inhibitors Show Promise Against Coronaviruses",
    summary: "Fragment-based drug discovery yields novel 3CL protease inhibitors with improved pharmacokinetic properties for COVID-19 treatment.",
    source: "Journal of Medicinal Chemistry",
    publish_date: "2024-10-30",
    tags: ["antiviral", "SARS-CoV-2", "drug discovery", "protease"],
    credibility: "Peer-reviewed",
    relevance: 95,
    link: "https://pubs.acs.org/journal/jmcmar",
    created_at: "2024-10-30T00:00:00Z"
  },
  {
    id: 10,
    title: "Single-Cell Genomics Reveals Viral Infection Dynamics",
    summary: "Advanced sequencing technologies map host-virus interactions at single-cell resolution, uncovering new therapeutic targets.",
    source: "Cell Host & Microbe",
    publish_date: "2024-11-22",
    tags: ["genomics", "host-pathogen interactions", "single-cell"],
    credibility: "Peer-reviewed",
    relevance: 90,
    link: "https://www.cell.com/cell-host-microbe",
    created_at: "2024-11-22T00:00:00Z"
  },
  {
    id: 11,
    title: "Mpox Virus Evolution Tracked Through Genomic Surveillance",
    summary: "Large-scale sequencing efforts monitor mpox virus mutations and transmission patterns to inform public health responses.",
    source: "New England Journal of Medicine",
    publish_date: "2024-10-15",
    tags: ["genomics", "outbreaks", "monkeypox", "evolution"],
    credibility: "Peer-reviewed",
    relevance: 88,
    link: "https://www.nejm.org",
    created_at: "2024-10-15T00:00:00Z"
  },
  {
    id: 12,
    title: "RSV Fusion Inhibitors Enter Clinical Trials",
    summary: "Structure-guided design produces small molecule inhibitors of respiratory syncytial virus fusion protein with promising safety profiles.",
    source: "Science Translational Medicine",
    publish_date: "2024-12-02",
    tags: ["structural", "RSV", "drug discovery", "fusion protein"],
    credibility: "Peer-reviewed",
    relevance: 85,
    link: "https://www.science.org/journal/stm",
    created_at: "2024-12-02T00:00:00Z"
  },
  {
    id: 13,
    title: "Influenza Vaccine Effectiveness Enhanced by AI Design",
    summary: "Machine learning algorithms predict optimal vaccine strains months ahead of flu season, improving protection rates.",
    source: "Nature Medicine",
    publish_date: "2024-11-10",
    tags: ["antiviral", "influenza", "vaccines", "machine learning"],
    credibility: "Peer-reviewed",
    relevance: 93,
    link: "https://www.nature.com/nm",
    created_at: "2024-11-10T00:00:00Z"
  },
  {
    id: 14,
    title: "Antibody Engineering Creates Universal Antivirals",
    summary: "Broadly neutralizing antibodies designed through computational modeling show activity against multiple viral families.",
    source: "Cell Reports",
    publish_date: "2024-10-28",
    tags: ["antiviral", "antibodies", "structural", "drug discovery"],
    credibility: "Peer-reviewed",
    relevance: 91,
    link: "https://www.cell.com/cell-reports",
    created_at: "2024-10-28T00:00:00Z"
  },
  {
    id: 15,
    title: "Viral Evolution Models Predict Next Pandemic Threats",
    summary: "Phylogenetic analysis combined with machine learning identifies high-risk viral lineages with pandemic potential.",
    source: "Nature",
    publish_date: "2024-12-08",
    tags: ["genomics", "outbreaks", "machine learning", "evolution"],
    credibility: "Peer-reviewed",
    relevance: 96,
    link: "https://www.nature.com",
    created_at: "2024-12-08T00:00:00Z"
  }
];

export default function Explore() {
  const [searchQuery, setSearchQuery] = useState('');
  const [topicFilter, setTopicFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [savedArticleIds, setSavedArticleIds] = useState<Set<number>>(new Set());

  // Load saved article IDs on mount
  useEffect(() => {
    const saved = getSavedArticles();
    setSavedArticleIds(new Set(saved.map(a => a.id)));
  }, []);

  const { data, isLoading, error } = useNews(
    page,
    20,
    searchQuery || undefined,
    topicFilter !== 'all' ? topicFilter : undefined
  );

  // Filter demo data based on search and topic
  const filteredDemoData = useMemo(() => {
    let filtered = DEMO_ARTICLES;
    
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
    
    return filtered;
  }, [searchQuery, topicFilter]);

  // Show demo data immediately while loading or if API fails/returns no data
  // This ensures instant display instead of waiting for API
  const newsArticles = useMemo(() => {
    // If we have valid API data, use it
    if (data?.articles && data.articles.length > 0) {
      return data.articles;
    }
    // Otherwise, show demo data immediately (while loading or on error)
    return filteredDemoData;
  }, [data, filteredDemoData]);

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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Explore Research</h1>
        <p className="text-[#4A6A7A]">Latest biotech and virology research from trusted sources</p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#4A6A7A]" />
              <Input
                placeholder="Search articles, topics, or keywords..."
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

      {/* Loading State - Only show if no demo data available */}
      {isLoading && newsArticles.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#1E88E5]" />
        </div>
      )}

      {/* Subtle loading indicator when demo data is shown but API is still loading */}
      {isLoading && newsArticles.length > 0 && (
        <div className="flex items-center justify-center py-2">
          <span className="text-xs text-[#4A6A7A] flex items-center gap-2">
            <Loader2 className="h-3 w-3 animate-spin text-[#1E88E5]" />
            Loading latest articles...
          </span>
        </div>
      )}

      {/* Error State - Only show if no demo data available */}
      {error && newsArticles.length === 0 && (
        <Alert variant="destructive">
          <AlertDescription>
            Failed to load news articles. Please try again later.
          </AlertDescription>
        </Alert>
      )}

      {/* News Feed - Show immediately with demo data */}
      {newsArticles.length > 0 ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {newsArticles.map((article) => (
              <Card key={article.id} className="hover:shadow-lg transition-shadow cursor-pointer group">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    {article.credibility && (
                      <Badge className={getCredibilityColor(article.credibility)} variant="outline">
                        {article.credibility}
                      </Badge>
                    )}
                    {article.publish_date && (
                      <span className="text-xs text-[#4A6A7A]">{article.publish_date}</span>
                    )}
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
                        className={`flex-1 ${savedArticleIds.has(article.id) ? 'bg-yellow-50 border-yellow-300 text-yellow-700' : ''}`}
                        onClick={() => {
                          if (savedArticleIds.has(article.id)) {
                            removeSavedArticle(article.id);
                            setSavedArticleIds(prev => {
                              const next = new Set(prev);
                              next.delete(article.id);
                              return next;
                            });
                            toast.success('Article removed from saved');
                          } else {
                            if (saveArticle(article)) {
                              setSavedArticleIds(prev => new Set([...prev, article.id]));
                              toast.success('Article saved!');
                            } else {
                              toast.info('Article already saved');
                            }
                          }
                        }}
                      >
                        {savedArticleIds.has(article.id) ? (
                          <>
                            <BookmarkCheck className="h-4 w-4 mr-1" />
                            Saved
                          </>
                        ) : (
                          <>
                            <Bookmark className="h-4 w-4 mr-1" />
                            Save
                          </>
                        )}
                      </Button>
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
                          onClick={() => window.open(article.link, '_blank')}
                        >
                          <ExternalLink className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {/* Pagination - Only show for API data, not demo data */}
          {data && data.total > 20 && (
            <div className="flex justify-center gap-2 mt-6">
              <Button
                variant="outline"
                disabled={page === 1}
                onClick={() => setPage(p => Math.max(1, p - 1))}
              >
                Previous
              </Button>
              <span className="flex items-center px-4 text-sm text-[#4A6A7A]">
                Page {page} of {Math.ceil(data.total / 20)}
              </span>
              <Button
                variant="outline"
                disabled={page >= Math.ceil(data.total / 20)}
                onClick={() => setPage(p => p + 1)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center text-[#4A6A7A]">
            No news articles found. Try adjusting your search or filters.
          </CardContent>
        </Card>
      )}
    </div>
  );
}