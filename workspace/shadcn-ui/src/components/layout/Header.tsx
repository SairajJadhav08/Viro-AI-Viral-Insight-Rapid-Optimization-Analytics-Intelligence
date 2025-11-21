import { Button } from '@/components/ui/button';
import { Menu, Bell, LogOut } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { useCurrentUser } from '@/hooks/use-auth';
import { useSignOut } from '@/hooks/use-auth';
import { useMemo, useEffect, useState } from 'react';
import type { User } from '@/lib/api/auth';

interface HeaderProps {
  onMenuClick: () => void;
}

// Demo user for fallback
const DEMO_USER: Partial<User> = {
  first_name: 'Research',
  last_name: 'User',
  role: 'Researcher',
};

export default function Header({ onMenuClick }: HeaderProps) {
  const navigate = useNavigate();
  const { data: user } = useCurrentUser();
  const signOut = useSignOut();
  const [refreshKey, setRefreshKey] = useState(0);

  // Listen for storage changes to update header when profile is saved
  useEffect(() => {
    const handleStorageChange = () => {
      setRefreshKey(prev => prev + 1);
    };
    window.addEventListener('storage', handleStorageChange);
    // Also listen for custom event for same-tab updates
    window.addEventListener('profileUpdated', handleStorageChange);
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('profileUpdated', handleStorageChange);
    };
  }, []);

  // Get user display info - prioritize localStorage, then API user, then demo
  const displayUser = useMemo(() => {
    const savedProfile = localStorage.getItem('profile_data');
    if (savedProfile) {
      try {
        const parsed = JSON.parse(savedProfile);
        return {
          first_name: parsed.first_name || DEMO_USER.first_name || '',
          last_name: parsed.last_name || DEMO_USER.last_name || '',
          avatar_url: parsed.avatar_url,
        };
      } catch (e) {
        // If parsing fails, fall through
      }
    }
    if (user) {
      return {
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        avatar_url: user.avatar_url,
      };
    }
    return {
      first_name: DEMO_USER.first_name || '',
      last_name: DEMO_USER.last_name || '',
      avatar_url: undefined,
    };
  }, [user, refreshKey]);

  const displayName = `${displayUser.first_name || ''} ${displayUser.last_name || ''}`.trim() || 'User';
  const initials = `${displayUser.first_name?.[0] || ''}${displayUser.last_name?.[0] || ''}`.toUpperCase() || 'U';

  return (
    <header className="sticky top-0 z-30 bg-card border-b border-border px-6 py-4">
      <div className="flex items-center justify-between">
        <Button variant="ghost" size="icon" onClick={onMenuClick} className="lg:hidden">
          <Menu className="h-6 w-6" />
        </Button>

        <div className="flex-1" />

        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage src={displayUser.avatar_url || undefined} />
                  <AvatarFallback className="bg-primary text-primary-foreground">{initials}</AvatarFallback>
                </Avatar>
                <span className="hidden md:inline text-foreground">{displayName}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
              <DropdownMenuLabel>My Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => navigate('/dashboard/profile')}>
                Profile
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => navigate('/dashboard/settings')}>
                Settings
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => signOut.mutate()} className="text-destructive">
                <LogOut className="h-4 w-4 mr-2" />
                Sign Out
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}