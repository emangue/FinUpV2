'use client';

import { Goal } from '@/types';

interface DonutChartProps {
  goals: Goal[];
}

export default function DonutChart({ goals }: DonutChartProps) {
  const totalBudget = goals.reduce((sum, goal) => sum + goal.budget, 0);
  const totalSpent = goals.reduce((sum, goal) => sum + goal.spent, 0);
  const overallPercentage = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0;

  // SVG donut chart calculations
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  
  let currentOffset = 0;
  const segments = goals.map((goal) => {
    const percentage = (goal.budget / totalBudget) * 100;
    const segmentLength = (circumference * percentage) / 100;
    const offset = currentOffset;
    currentOffset += segmentLength;
    
    return {
      goal,
      percentage,
      offset,
      length: segmentLength,
      color: getSegmentColor(goal.color)
    };
  });

  function getSegmentColor(color: string): string {
    const colors: Record<string, string> = {
      blue: '#3b82f6',
      green: '#10b981',
      orange: '#f97316',
      pink: '#ec4899',
      purple: '#a855f7'
    };
    return colors[color] || colors.blue;
  }

  return (
    <div className="relative w-48 h-48 mx-auto">
      <svg className="transform -rotate-90" width="192" height="192" viewBox="0 0 192 192">
        {/* Background circle */}
        <circle
          cx="96"
          cy="96"
          r={radius}
          fill="none"
          stroke="#f3f4f6"
          strokeWidth="14"
        />
        
        {/* Goal segments */}
        {segments.map((segment, index) => (
          <circle
            key={index}
            cx="96"
            cy="96"
            r={radius}
            fill="none"
            stroke={segment.color}
            strokeWidth="16"
            strokeLinecap="round"
            strokeDasharray={`${segment.length} ${circumference - segment.length}`}
            strokeDashoffset={-segment.offset}
            className="cursor-pointer hover:opacity-80 transition-all duration-500"
          />
        ))}
      </svg>
      
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-[9px] uppercase tracking-wider text-gray-400 font-semibold mb-0.5">Fevereiro 2026</p>
        <div className="flex items-start">
          <span className="text-3xl font-bold text-gray-800">R$ {Math.floor(totalSpent / 1000)}</span>
          <span className="text-xl font-bold text-gray-400 ml-0.5">.{String(totalSpent).slice(-3)}</span>
        </div>
        <p className="text-[10px] text-gray-400 mt-0.5">
          de R$ {totalBudget.toLocaleString('pt-BR')}
        </p>
      </div>
    </div>
  );
}
