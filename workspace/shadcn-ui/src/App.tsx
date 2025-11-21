import { Toaster } from '@/components/ui/sonner';
import { TooltipProvider } from '@/components/ui/tooltip';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'next-themes';
import Index from './pages/Index';
import Login from './pages/Login';
import DashboardLayout from './components/layout/DashboardLayout';
import Explore from './pages/dashboard/Explore';
import NewProject from './pages/dashboard/NewProject';
import Result from './pages/dashboard/Result';
import History from './pages/dashboard/History';
import Overview from './pages/dashboard/Overview';
import Profile from './pages/dashboard/Profile';
import Settings from './pages/dashboard/Settings';
import Help from './pages/dashboard/Help';
import SavedArticles from './pages/dashboard/SavedArticles';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Don't show error toasts for queries by default
      // Individual queries can handle their own error display
      retry: (failureCount, error: any) => {
        // Don't retry on 4xx errors (client errors)
        if (error?.status >= 400 && error?.status < 500) {
          return false;
        }
        return failureCount < 2;
      },
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
      <TooltipProvider>
        <Toaster />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/dashboard" element={<DashboardLayout />}>
              <Route index element={<Navigate to="/dashboard/explore" replace />} />
              <Route path="explore" element={<Explore />} />
              <Route path="new-project" element={<NewProject />} />
              <Route path="result" element={<Result />} />
              <Route path="history" element={<History />} />
              <Route path="overview" element={<Overview />} />
              <Route path="saved-articles" element={<SavedArticles />} />
              <Route path="profile" element={<Profile />} />
              <Route path="settings" element={<Settings />} />
              <Route path="help" element={<Help />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;