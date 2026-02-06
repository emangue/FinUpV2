'use client';

import { Goal, GoalType } from '@/types';
import GoalCard from '../molecules/GoalCard';

interface GoalsListProps {
  goals: Goal[];
  filterType?: GoalType | 'todas';
}

export default function GoalsList({ goals, filterType = 'todas' }: GoalsListProps) {
  const filteredGoals = filterType === 'todas' 
    ? goals 
    : goals.filter(goal => goal.type === filterType);

  if (filteredGoals.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-gray-400 text-sm">Nenhuma meta encontrada</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {filteredGoals.map((goal) => (
        <GoalCard key={goal.id} goal={goal} />
      ))}
    </div>
  );
}
