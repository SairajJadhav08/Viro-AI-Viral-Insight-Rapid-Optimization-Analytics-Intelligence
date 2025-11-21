import { useMemo, useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { FileText, TrendingUp, Clock, CheckCircle, PlusCircle, Play, Download, Users, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useProjects } from '@/hooks/use-projects';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';

// Helper to get saved articles count
const getSavedArticlesCount = (): number => {
  if (typeof window === 'undefined') return 0;
  const saved = localStorage.getItem('saved_articles');
  return saved ? JSON.parse(saved).length : 0;
};

export default function Overview() {
  const navigate = useNavigate();
  const { data, isLoading, error } = useProjects(1, 100); // Get more projects for stats
  const [savedArticlesCount, setSavedArticlesCount] = useState(0);

  // Load saved articles count
  useEffect(() => {
    const updateCount = () => {
      setSavedArticlesCount(getSavedArticlesCount());
    };
    updateCount();
    
    // Listen for storage changes
    const handleStorageChange = () => {
      updateCount();
    };
    window.addEventListener('storage', handleStorageChange);
    
    // Check periodically for same-tab updates
    const interval = setInterval(updateCount, 1000);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  const stats = useMemo(() => {
    if (!data?.projects) return [
      { label: 'Projects Created', value: '0', icon: FileText, color: 'text-blue-600' },
      { label: 'Runs Completed', value: '0', icon: CheckCircle, color: 'text-green-600' },
      { label: 'Publications Saved', value: savedArticlesCount.toString(), icon: TrendingUp, color: 'text-purple-600' },
      { label: 'Active Experiments', value: '0', icon: Clock, color: 'text-orange-600' }
    ];

    const totalProjects = data.total || data.projects.length;
    const completedProjects = data.projects.filter(p => p.status === 'Completed').length;
    const activeProjects = data.projects.filter(p => p.status === 'Processing').length;

    return [
      { label: 'Projects Created', value: totalProjects.toString(), icon: FileText, color: 'text-blue-600' },
      { label: 'Runs Completed', value: completedProjects.toString(), icon: CheckCircle, color: 'text-green-600' },
      { label: 'Publications Saved', value: savedArticlesCount.toString(), icon: TrendingUp, color: 'text-purple-600' },
      { label: 'Active Experiments', value: activeProjects.toString(), icon: Clock, color: 'text-orange-600' }
    ];
  }, [data, savedArticlesCount]);

  const recentProjects = useMemo(() => {
    if (!data?.projects) return [];
    return data.projects
      .slice(0, 3)
      .map(project => ({
        name: project.title,
        progress: project.status === 'Completed' ? 100 : project.status === 'Processing' ? 50 : 0,
        status: project.status
      }));
  }, [data?.projects]);

  const kpis = useMemo(() => {
    if (!data?.projects) return {
      quarterProjects: 0,
      avgCompletion: '0 days',
      successRate: '0%',
      avgDeadliness: 0,
      reports: 0,
      structures: 0,
      datasets: 0
    };

    const completedProjects = data.projects.filter(p => p.status === 'Completed');
    const quarterProjects = data.projects.length; // Simplified - would need date filtering
    const successRate = data.projects.length > 0 
      ? ((completedProjects.length / data.projects.length) * 100).toFixed(1) 
      : '0';
    
    // Calculate average completion time (simplified - would need created_at and updated_at)
    const avgCompletion = 'N/A';

    return {
      quarterProjects,
      avgCompletion,
      successRate: `${successRate}%`,
      avgDeadliness: 0, // Would need to fetch results for all projects
      reports: 0,
      structures: 0,
      datasets: 0
    };
  }, [data?.projects]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[#0B2336] mb-2">Research Overview</h1>
          <p className="text-[#4A6A7A]">Your personal research dashboard</p>
        </div>
        <Button onClick={() => navigate('/dashboard/new-project')} className="bg-[#1E88E5] hover:bg-[#0B4F8C]">
          <PlusCircle className="h-4 w-4 mr-2" />
          New Project
        </Button>
      </div>

      {/* Stats Grid - Show immediately with data or defaults */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card 
            key={index}
            className={stat.label === 'Publications Saved' ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''}
            onClick={stat.label === 'Publications Saved' ? () => navigate('/dashboard/saved-articles') : undefined}
          >
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-[#4A6A7A] mb-1">{stat.label}</p>
                  <p className="text-3xl font-bold text-[#0B2336]">{stat.value}</p>
                </div>
                <stat.icon className={`h-12 w-12 ${stat.color}`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Projects */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Projects</CardTitle>
            <CardDescription>Progress on your latest research</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-[#1E88E5]" />
              </div>
            ) : recentProjects.length === 0 ? (
              <p className="text-sm text-[#4A6A7A] text-center py-4">No projects yet. Create your first project to get started.</p>
            ) : (
              recentProjects.map((project, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-[#0B2336]">{project.name}</span>
                    <span className={`text-xs px-2 py-1 rounded ${
                      project.status === 'Completed' ? 'bg-green-100 text-green-800' :
                      project.status === 'Processing' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>{project.status}</span>
                  </div>
                  <Progress value={project.progress} className="h-2" />
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start" onClick={() => navigate('/dashboard/new-project')}>
              <PlusCircle className="h-4 w-4 mr-2" />
              Start New Project
            </Button>
            <Button variant="outline" className="w-full justify-start" onClick={() => navigate('/dashboard/history')}>
              <Play className="h-4 w-4 mr-2" />
              View Project History
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                // Export all projects data
                if (!data?.projects || data.projects.length === 0) {
                  toast.error('No projects to export');
                  return;
                }
                
                try {
                  const exportData = {
                    exported_at: new Date().toISOString(),
                    total_projects: data.projects.length,
                    projects: data.projects.map(p => ({
                      id: p.id,
                      title: p.title,
                      status: p.status,
                      created_at: p.created_at,
                      country: p.country,
                      region: p.region,
                    })),
                  };
                  
                  const jsonStr = JSON.stringify(exportData, null, 2);
                  const blob = new Blob([jsonStr], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const link = document.createElement('a');
                  link.href = url;
                  link.download = `VIRO-AI_Projects_Export_${new Date().toISOString().split('T')[0]}.json`;
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  URL.revokeObjectURL(url);
                  
                  toast.success('Projects exported successfully!');
                } catch (error) {
                  console.error('Export error:', error);
                  toast.error('Failed to export projects');
                }
              }}
            >
              <Download className="h-4 w-4 mr-2" />
              Schedule Export
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => {
                toast.info('Expert review feature coming soon! For now, please use the contact form in Help section.');
                navigate('/dashboard/help');
              }}
            >
              <Users className="h-4 w-4 mr-2" />
              Request Expert Review
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Research Backlog */}
      <Card>
        <CardHeader>
          <CardTitle>Research Backlog</CardTitle>
          <CardDescription>Pending tasks and action items</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <p className="text-sm text-[#4A6A7A] text-center py-4">No pending tasks at this time.</p>
          </div>
        </CardContent>
      </Card>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">This Quarter</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-[#4A6A7A]">Projects</span>
                  <span className="font-semibold">{kpis.quarterProjects}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#4A6A7A]">Avg. Completion</span>
                  <span className="font-semibold">{kpis.avgCompletion}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#4A6A7A]">Success Rate</span>
                  <span className="font-semibold text-green-600">{kpis.successRate}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Avg. Deadliness Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center">
                <div className="text-4xl font-bold text-[#0B4F8C]">
                  {kpis.avgDeadliness > 0 ? kpis.avgDeadliness.toFixed(1) : 'N/A'}
                </div>
                <p className="text-sm text-[#4A6A7A] mt-2">Across all projects</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Exports</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-[#4A6A7A]">Reports</span>
                  <span className="font-semibold">{kpis.reports}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#4A6A7A]">Structures</span>
                  <span className="font-semibold">{kpis.structures}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-[#4A6A7A]">Datasets</span>
                  <span className="font-semibold">{kpis.datasets}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
    </div>
  );
}