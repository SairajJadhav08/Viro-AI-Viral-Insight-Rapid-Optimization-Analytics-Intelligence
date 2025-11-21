import { useState, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Calendar, MapPin, TrendingUp, Loader2, Trash2, RefreshCw, PlusCircle } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useNavigate } from 'react-router-dom';
import { useProjects, useDeleteProject } from '@/hooks/use-projects';
import { useProjectResults } from '@/hooks/use-results';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import type { Project } from '@/lib/api/projects';

// Component to render project card with results data
function ProjectCardWithResults({ 
  project, 
  formattedDate, 
  projectId, 
  navigate, 
  getStatusColor,
  onDelete
}: { 
  project: Project; 
  formattedDate: string; 
  projectId: string; 
  navigate: (path: string) => void; 
  getStatusColor: (status: string) => string;
  onDelete: (id: number) => void;
}) {
  const { data: results } = useProjectResults(project.status === 'Completed' ? project.id : null);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  
  const deadlinessScore = results?.project?.deadliness_score;
  const topCandidate = results?.drugs?.[0]?.drug_name;

  const handleDeleteClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete(project.id);
    setShowDeleteDialog(false);
  };

  return (
    <>
      <Card 
        key={project.id} 
        className="hover:shadow-lg transition-shadow cursor-pointer relative" 
        onClick={() => navigate(`/dashboard/result?projectId=${project.id}`)}
      >
        <CardHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <CardTitle className="text-lg">{project.title}</CardTitle>
                <Badge className={getStatusColor(project.status)} variant="outline">
                  {project.status}
                </Badge>
              </div>
              <CardDescription className="flex items-center gap-4 flex-wrap">
                {formattedDate && (
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formattedDate}
                  </span>
                )}
                {(project.region || project.country) && (
                  <span className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {[project.region, project.country].filter(Boolean).join(', ')}
                  </span>
                )}
                <span className="text-xs text-[#4A6A7A]">ID: {projectId}</span>
              </CardDescription>
            </div>
            <div className="flex items-center gap-3">
              {deadlinessScore && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{deadlinessScore}</div>
                  <p className="text-xs text-[#4A6A7A]">Score</p>
                </div>
              )}
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={handleDeleteClick}
                title="Delete project"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex gap-2">
              {project.mutations_count > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {project.mutations_count} Mutation{project.mutations_count !== 1 ? 's' : ''}
                </Badge>
              )}
              {project.drugs_count > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {project.drugs_count} Drug{project.drugs_count !== 1 ? 's' : ''}
                </Badge>
              )}
            </div>
            {topCandidate && (
              <div className="flex items-center gap-2 text-sm text-[#4A6A7A]">
                <TrendingUp className="h-4 w-4 text-[#1E88E5]" />
                <span>Top: {topCandidate}</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent onClick={(e) => e.stopPropagation()}>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Project</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{project.title}"? This action cannot be undone and will permanently delete all associated data, results, and files.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={(e) => e.stopPropagation()}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

export default function History() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [page, setPage] = useState(1);

  const { data, isLoading, error, refetch } = useProjects(page, 20);
  const deleteProject = useDeleteProject();

  const handleDeleteProject = (projectId: number) => {
    deleteProject.mutate(projectId);
  };

  const handleRefresh = () => {
    refetch();
  };

  const filteredProjects = useMemo(() => {
    if (!data?.projects) return [];
    
    let filtered = data.projects;

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(p => 
        p.status.toLowerCase() === statusFilter.toLowerCase()
      );
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(p => 
        p.title.toLowerCase().includes(query) ||
        p.id.toString().includes(query) ||
        p.country?.toLowerCase().includes(query) ||
        p.region?.toLowerCase().includes(query)
      );
    }

    return filtered;
  }, [data?.projects, statusFilter, searchQuery]);

  // Determine if we should show empty state immediately
  // Show immediately if we have data and filtered results are empty
  const hasNoProjects = useMemo(() => {
    // If we have data (even if loading is still true), check if filtered results are empty
    if (data?.projects !== undefined) {
      // If no search/filter applied, check if original data is empty
      if (searchQuery === '' && statusFilter === 'all') {
        return data.projects.length === 0;
      }
      // If search/filter applied, check filtered results
      return filteredProjects.length === 0;
    }
    // If we don't have data yet, don't show empty state (show loading instead)
    return false;
  }, [data, filteredProjects, searchQuery, statusFilter]);

  // Calculate summary statistics
  const summaryStats = useMemo(() => {
    if (!data?.projects) {
      return {
        total: 0,
        completed: 0,
        processing: 0,
        pending: 0
      };
    }
    
    return {
      total: data.projects.length,
      completed: data.projects.filter(p => p.status === 'Completed').length,
      processing: data.projects.filter(p => p.status === 'Processing').length,
      pending: data.projects.filter(p => p.status === 'Pending' || p.status === 'Failed').length
    };
  }, [data?.projects]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'Processing':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'Failed':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Refresh Button */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Project History</h1>
          <p className="text-[#4A6A7A]">View and manage your past viral analysis projects</p>
        </div>
        <Button
          variant="outline"
          onClick={handleRefresh}
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-[#4A6A7A]" />
              <Input
                placeholder="Search by project title or ID..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="All Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="processing">Processing</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading State - Only show if we don't have data yet */}
      {isLoading && !data && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-[#1E88E5]" />
        </div>
      )}

      {/* Project List or Empty State - Show immediately when we have data (even if still loading) */}
      {(data || (!isLoading && !error)) && (
        <>
          {(hasNoProjects || (data && (!data.projects || data.projects.length === 0))) ? (
            <Card className="border-2 border-dashed border-[#EAF3FF]">
              <CardContent className="pt-16 pb-16">
                <div className="flex flex-col items-center justify-center text-center space-y-6">
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold text-[#0B2336]">
                      No projects yet. Create your first analysis project!
                    </h3>
                    <p className="text-[#4A6A7A] max-w-md">
                      {searchQuery || statusFilter !== 'all' 
                        ? 'No projects match your search criteria. Try adjusting your filters.' 
                        : 'Get started by creating a new viral analysis project to explore mutations, drug candidates, and modifications.'}
                    </p>
                  </div>
                  {(!searchQuery && statusFilter === 'all') && (
                    <Button
                      onClick={() => navigate('/dashboard/new-project')}
                      className="bg-[#0B4F8C] hover:bg-[#0A3D6F] text-white px-8 py-6 text-base"
                      size="lg"
                    >
                      <PlusCircle className="h-5 w-5 mr-2" />
                      Create New Project
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredProjects.map((project) => {
                const formattedDate = project.created_at ? new Date(project.created_at).toISOString().split('T')[0] : '';
                const projectId = `PRJ-${project.id}`;
                
                return (
                  <ProjectCardWithResults 
                    key={project.id} 
                    project={project}
                    formattedDate={formattedDate}
                    projectId={projectId}
                    navigate={navigate}
                    getStatusColor={getStatusColor}
                    onDelete={handleDeleteProject}
                  />
                );
              })}
            </div>
          )}
          {/* Pagination */}
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
      )}

      {/* Summary Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-[#1E88E5] mb-1">{summaryStats.total}</div>
              <p className="text-sm text-[#4A6A7A]">Total Projects</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">{summaryStats.completed}</div>
              <p className="text-sm text-[#4A6A7A]">Completed</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-500 mb-1">{summaryStats.processing}</div>
              <p className="text-sm text-[#4A6A7A]">Processing</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-gray-600 mb-1">{summaryStats.pending}</div>
              <p className="text-sm text-[#4A6A7A]">Pending</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
