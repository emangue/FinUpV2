'use client';

import { useRouter } from 'next/navigation';
import { Goal } from '@/types';
import GoalIcon from '../atoms/GoalIcon';

interface GoalListItemProps {
  goal: Goal;
  onToggle: (id: string) => void;
  onEdit: (id: string) => void;
}

export default function GoalListItem({ goal, onToggle, onEdit }: GoalListItemProps) {
  return (
    <div className="p-4 bg-gray-50 rounded-2xl border-2 border-transparent hover:border-blue-200 transition-all" style={{ opacity: goal.active ? 1 : 0.5 }}>
      <div className="flex items-center gap-3">
        {/* Drag Handle */}
        <button className="drag-handle text-gray-400 hover:text-gray-600 cursor-grab active:cursor-grabbing">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
          </svg>
        </button>
        
        <GoalIcon icon={goal.icon} color={goal.color} size="md" />
        
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-gray-900">{goal.name}</h3>
          <p className="text-xs text-gray-500">
            {goal.type === 'investimento' && goal.deadline 
              ? `R$ ${goal.budget.toLocaleString()} até ${goal.deadline}`
              : `R$ ${goal.budget.toLocaleString()}/mês`
            }
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Toggle Active */}
          <label className="relative inline-flex items-center cursor-pointer">
            <input 
              type="checkbox" 
              checked={goal.active}
              onChange={() => onToggle(goal.id)}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
          
          {/* Edit Button */}
          <button 
            onClick={() => onEdit(goal.id)}
            className="text-gray-400 hover:text-blue-600 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
