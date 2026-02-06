'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { GoalType } from '@/types';
import { mockGoals, months } from '@/lib/constants';
import HeaderBar from '../molecules/HeaderBar';
import MonthScroll from '../molecules/MonthScroll';
import TabBar from '../molecules/TabBar';
import DonutChart from '../organisms/DonutChart';
import GoalsList from '../organisms/GoalsList';
import IconButton from '../atoms/IconButton';

export default function MetasLayout() {
  const router = useRouter();
  const [selectedMonth, setSelectedMonth] = useState('fev');
  const [activeTab, setActiveTab] = useState<GoalType | 'todas'>('todas');
  const [goals] = useState(mockGoals.filter(g => g.active));

  const handleManage = () => {
    router.push('/gerenciar-metas');
  };

  const filteredGoals = activeTab === 'todas' 
    ? goals 
    : goals.filter(goal => goal.type === activeTab);

  return (
    <div className="w-full max-w-md mx-auto animate-fade-in">
      <HeaderBar
        title="Metas"
        onBack={() => router.back()}
        rightAction={
          <IconButton onClick={handleManage}>
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
          </IconButton>
        }
      />

      <MonthScroll
        months={months}
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
      />

      <div className="bg-white px-6 pb-6 rounded-b-3xl">
        <div className="py-6">
          <DonutChart goals={filteredGoals} />
        </div>

        <div className="mb-6">
          <TabBar
            activeTab={activeTab}
            onTabChange={setActiveTab}
          />
        </div>

        <GoalsList goals={goals} filterType={activeTab} />
      </div>
    </div>
  );
}
