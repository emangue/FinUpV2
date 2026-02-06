'use client';

import { GoalType } from '@/types';

interface TabBarProps {
  activeTab: GoalType | 'todas';
  onTabChange: (tab: GoalType | 'todas') => void;
}

export default function TabBar({ activeTab, onTabChange }: TabBarProps) {
  return (
    <div className="flex gap-6 border-b border-gray-200">
      <button
        onClick={() => onTabChange('gasto')}
        className={`pb-2 text-sm font-semibold transition-colors ${
          activeTab === 'gasto'
            ? 'text-gray-900 border-b-2 border-gray-900'
            : 'text-gray-400 hover:text-gray-600'
        }`}
      >
        Gastos
      </button>
      <button
        onClick={() => onTabChange('investimento')}
        className={`pb-2 text-sm font-semibold transition-colors ${
          activeTab === 'investimento'
            ? 'text-gray-900 border-b-2 border-gray-900'
            : 'text-gray-400 hover:text-gray-600'
        }`}
      >
        Investimento
      </button>
      <button
        onClick={() => onTabChange('todas')}
        className={`pb-2 text-sm font-semibold transition-colors ${
          activeTab === 'todas'
            ? 'text-gray-900 border-b-2 border-gray-900'
            : 'text-gray-400 hover:text-gray-600'
        }`}
      >
        Todas
      </button>
    </div>
  );
}
