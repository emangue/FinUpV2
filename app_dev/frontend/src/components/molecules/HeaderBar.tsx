import { Avatar } from '@/components/atoms/Avatar';
import { MonthSelector } from '@/components/atoms/MonthSelector';
import { Search } from 'lucide-react';

interface HeaderBarProps {
  title: string;
  avatarSrc: string;
  selectedMonth: string;
  onMonthChange?: (month: string) => void;
}

export function HeaderBar({
  title,
  avatarSrc,
  selectedMonth,
  onMonthChange
}: HeaderBarProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      {/* Título */}
      <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
      
      {/* Controles à direita */}
      <div className="flex items-center gap-4">
        <button className="text-gray-400 hover:text-gray-600">
          <Search size={20} />
        </button>
        <MonthSelector
          selectedMonth={selectedMonth}
          onChange={onMonthChange}
        />
        <Avatar src={avatarSrc} alt="User avatar" size={40} />
      </div>
    </div>
  );
}
