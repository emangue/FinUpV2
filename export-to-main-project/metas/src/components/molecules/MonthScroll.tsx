'use client';

import MonthButton from '../atoms/MonthButton';
import { Month } from '@/types';

interface MonthScrollProps {
  months: Month[];
  selectedMonth: string;
  onMonthChange: (month: string) => void;
}

export default function MonthScroll({ months, selectedMonth, onMonthChange }: MonthScrollProps) {
  return (
    <div className="px-6 py-4 overflow-x-auto scrollbar-hide">
      <div className="flex gap-3 min-w-max">
        {months.map((month) => (
          <MonthButton
            key={month.value}
            label={month.label}
            year={month.year}
            active={selectedMonth === month.value}
            onClick={() => onMonthChange(month.value)}
          />
        ))}
      </div>
    </div>
  );
}
