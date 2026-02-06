import { ChevronDown } from 'lucide-react';

interface MonthSelectorProps {
  selectedMonth: string; // "September 2026"
  onChange?: (month: string) => void;
}

export function MonthSelector({ selectedMonth, onChange }: MonthSelectorProps) {
  return (
    <button
      onClick={() => onChange?.(selectedMonth)}
      className="flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
    >
      <span>{selectedMonth.split(' ')[0]}</span>
      <ChevronDown size={16} />
    </button>
  );
}
