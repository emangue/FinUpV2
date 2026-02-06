'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { mockGoals } from '@/lib/constants';
import HeaderBar from '../molecules/HeaderBar';
import GoalListItem from '../molecules/GoalListItem';

export default function GerenciarLayout() {
  const router = useRouter();
  const [goals, setGoals] = useState(mockGoals);

  const handleToggle = (id: string) => {
    setGoals(goals.map(g => g.id === id ? { ...g, active: !g.active } : g));
  };

  const handleEdit = (id: string) => {
    router.push('/editar-meta');
  };

  const handleSave = () => {
    alert('Alterações salvas!');
    router.back();
  };

  const handleNewGoal = () => {
    router.push('/editar-meta');
  };

  const gastosGoals = goals.filter(g => g.type === 'gasto');
  const investimentosGoals = goals.filter(g => g.type === 'investimento');

  return (
    <div className="w-full max-w-md mx-auto animate-fade-in">
      <HeaderBar
        title="Gerenciar Metas"
        onBack={() => router.back()}
        rightAction={
          <button
            onClick={handleSave}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors"
          >
            Salvar
          </button>
        }
      />

      <div className="bg-white px-6 pt-2 pb-6">
        <p className="text-xs text-gray-400 text-right mb-4">Fevereiro 2026</p>

        <div className="pb-4">
          <p className="text-xs text-gray-500">
            Arraste para reordenar, ative/desative ou edite cada meta individualmente
          </p>
        </div>

        {/* Goals List */}
        <div className="space-y-3">
          {gastosGoals.map((goal) => (
            <GoalListItem
              key={goal.id}
              goal={goal}
              onToggle={handleToggle}
              onEdit={handleEdit}
            />
          ))}

          {/* Divider */}
          <div className="py-2">
            <div className="border-t border-gray-200"></div>
            <p className="text-xs text-gray-400 text-center py-2">Investimentos</p>
          </div>

          {investimentosGoals.map((goal) => (
            <GoalListItem
              key={goal.id}
              goal={goal}
              onToggle={handleToggle}
              onEdit={handleEdit}
            />
          ))}
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="px-6 pb-6">
        <button
          onClick={handleNewGoal}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl py-4 font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          Nova Meta
        </button>
      </div>
    </div>
  );
}
