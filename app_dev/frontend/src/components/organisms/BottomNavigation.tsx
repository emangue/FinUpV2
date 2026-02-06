import { Home, BarChart3, User, Plus } from 'lucide-react';
import { IconButton } from '@/components/atoms/IconButton';

interface BottomNavigationProps {
  activeTab: 'home' | 'chart' | 'user';
  onTabChange?: (tab: string) => void;
}

export function BottomNavigation({
  activeTab,
  onTabChange
}: BottomNavigationProps) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-100 px-6 py-4">
      <div className="flex items-center justify-between max-w-md mx-auto">
        <IconButton
          icon={Home}
          label="Home"
          isActive={activeTab === 'home'}
          onClick={() => onTabChange?.('home')}
        />
        <IconButton
          icon={BarChart3}
          label="Chart"
          isActive={activeTab === 'chart'}
          onClick={() => onTabChange?.('chart')}
        />
        <IconButton
          icon={User}
          label="Profile"
          isActive={activeTab === 'user'}
          onClick={() => onTabChange?.('user')}
        />
        
        {/* FAB (Add button) */}
        <button
          onClick={() => onTabChange?.('add')}
          className="flex items-center justify-center w-14 h-14 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 transition-colors"
          aria-label="Add"
        >
          <Plus size={24} />
        </button>
      </div>
    </nav>
  );
}
