import { useState, useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import Chatbot from '@/components/ui/chatbot';
import { Loader2 } from 'lucide-react';

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    const checkAuth = () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
      
      if (!token || token.trim() === '') {
        // No token found, redirect to login
        navigate('/login', { replace: true });
      } else {
        // Token exists, allow access
        setIsCheckingAuth(false);
      }
    };
    
    // Check immediately
    checkAuth();
    
    // Also check after a small delay to handle race conditions with login
    // This gives time for the token to be stored after login
    const timeoutId = setTimeout(() => {
      checkAuth();
    }, 150);
    
    return () => clearTimeout(timeoutId);
  }, [navigate]);

  // Show loading state while checking authentication
  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-[#1E88E5]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className={`transition-all duration-300 ${sidebarOpen ? 'lg:ml-64' : 'lg:ml-20'}`}>
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
        <main className="p-6 bg-background">
          <Outlet />
        </main>
      </div>
      {/* Chatbot Widget - Available on all dashboard pages */}
      <Chatbot />
    </div>
  );
}