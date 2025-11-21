import { NavLink } from 'react-router-dom';
import { Dna, Compass, PlusCircle, FileText, History, LayoutDashboard, Settings, HelpCircle, User, Bookmark } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export default function Sidebar({ isOpen }: SidebarProps) {
  const navItems = [
    { icon: Compass, label: 'Explore', path: '/dashboard/explore' },
    { icon: PlusCircle, label: 'New Project', path: '/dashboard/new-project' },
    { icon: FileText, label: 'Results', path: '/dashboard/result' },
    { icon: History, label: 'History', path: '/dashboard/history' },
    { icon: LayoutDashboard, label: 'Overview', path: '/dashboard/overview' },
    { icon: Bookmark, label: 'Saved Articles', path: '/dashboard/saved-articles' },
    { icon: Settings, label: 'Settings', path: '/dashboard/settings' },
    { icon: HelpCircle, label: 'Help / Docs', path: '/dashboard/help' },
    { icon: User, label: 'My Profile', path: '/dashboard/profile' }
  ];

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-full bg-card border-r border-border transition-all duration-300 z-40',
        isOpen ? 'w-64' : 'w-20'
      )}
    >
      <div className="flex items-center gap-2 p-6 border-b border-border">
        <Dna className="h-8 w-8 text-primary flex-shrink-0" />
        {isOpen && <span className="text-xl font-bold text-foreground">VIRO-AI</span>}
      </div>

      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-accent text-accent-foreground font-medium'
                  : 'text-muted-foreground hover:bg-muted'
              )
            }
          >
            <item.icon className="h-5 w-5 flex-shrink-0" />
            {isOpen && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}