'use client';

import { useRouter } from 'next/navigation';
import { Goal } from '@/types';

interface GoalCardProps {
  goal: Goal;
}

export default function GoalCard({ goal }: GoalCardProps) {
  const router = useRouter();

  const handleClick = () => {
    router.push('/detalhes-meta');
  };

  const getColorClasses = (color: string) => {
    const colors: Record<string, { stroke: string; badge: string }> = {
      blue: { stroke: '#3B82F6', badge: 'bg-blue-100 text-blue-700' },
      green: { stroke: '#10B981', badge: 'bg-green-100 text-green-700' },
      orange: { stroke: '#F97316', badge: 'bg-orange-100 text-orange-700' },
      pink: { stroke: '#EC4899', badge: 'bg-pink-100 text-pink-700' },
      purple: { stroke: '#A855F7', badge: 'bg-purple-100 text-purple-700' }
    };
    return colors[color] || colors.blue;
  };

  const colorClasses = getColorClasses(goal.color);
  const remaining = goal.budget - goal.spent;
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (circumference * goal.percentage) / 100;

  const getTypeLabel = () => {
    return goal.type === 'gasto' ? 'Gasto' : 'Investimento';
  };

  const getTypeBadge = () => {
    return goal.type === 'gasto' 
      ? 'bg-orange-100 text-orange-700' 
      : 'bg-purple-100 text-purple-700';
  };

  const getPercentageColor = () => {
    if (goal.percentage >= 80) return 'text-red-600';
    if (goal.percentage >= 50) return 'text-orange-600';
    return 'text-green-600';
  };

  return (
    <div
      onClick={handleClick}
      className="p-4 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-all cursor-pointer"
    >
      <div className="flex items-start gap-4">
        {/* Progress Circle */}
        <div className="relative flex-shrink-0">
          <svg className="w-16 h-16 transform -rotate-90">
            <circle cx="32" cy="32" r={radius} fill="none" stroke="#E5E7EB" strokeWidth="4" />
            <circle
              cx="32"
              cy="32"
              r={radius}
              fill="none"
              stroke={colorClasses.stroke}
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className="transition-all duration-500"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-bold text-gray-700">{goal.percentage}%</span>
          </div>
        </div>

        {/* Goal Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <h3 className="text-sm font-bold text-gray-900">{goal.name}</h3>
            <span className={`px-2 py-0.5 ${getTypeBadge()} text-xs font-semibold rounded-full`}>
              {getTypeLabel()}
            </span>
          </div>
          <p className="text-xs text-gray-500 mb-2">{goal.description}</p>

          <div className="flex items-baseline gap-2 mb-2">
            <span className="text-base font-bold text-gray-900">
              R$ {goal.spent.toLocaleString('pt-BR')}
            </span>
            <span className="text-xs text-gray-400">
              de R$ {goal.budget.toLocaleString('pt-BR')}
            </span>
          </div>

          <div className="flex items-center justify-between text-xs">
            <span className="text-gray-500">
              Restante: R$ {remaining.toLocaleString('pt-BR')}
            </span>
            <span className={`font-semibold ${getPercentageColor()}`}>
              {goal.percentage}% usado
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

