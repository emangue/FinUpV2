'use client';

import { useRouter } from 'next/navigation';
import { mockGoals, mockTransactions } from '@/lib/constants';

export default function DetalhesLayout() {
  const router = useRouter();
  const goal = mockGoals[0]; // Mock - primeira meta

  const handleEdit = () => {
    router.push('/editar-meta');
  };

  const remaining = goal.budget - goal.spent;
  const radius = 70;
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

  const getIconColor = () => {
    const colors: Record<string, { bg: string; text: string }> = {
      blue: { bg: 'bg-blue-100', text: 'text-blue-600' },
      green: { bg: 'bg-green-100', text: 'text-green-600' },
      orange: { bg: 'bg-orange-100', text: 'text-orange-600' },
      pink: { bg: 'bg-pink-100', text: 'text-pink-600' },
      purple: { bg: 'bg-purple-100', text: 'text-purple-600' }
    };
    return colors[goal.color] || colors.blue;
  };

  const getStrokeColor = () => {
    const colors: Record<string, string> = {
      blue: '#3B82F6',
      green: '#10B981',
      orange: '#F97316',
      pink: '#EC4899',
      purple: '#A855F7'
    };
    return colors[goal.color] || colors.blue;
  };

  const iconColor = getIconColor();
  const strokeColor = getStrokeColor();

  return (
    <div className="w-full max-w-md mx-auto animate-fade-in">
      {/* Header */}
      <header className="bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100">
        <button onClick={() => router.back()} className="text-gray-700 hover:text-gray-900 transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <h1 className="text-lg font-bold text-gray-800">Detalhes</h1>
        <button onClick={handleEdit} className="text-gray-700 hover:text-gray-900 transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </button>
      </header>

      {/* Date */}
      <div className="bg-white px-6 py-2">
        <p className="text-xs text-gray-400 text-right">Fevereiro 2026</p>
      </div>

      {/* Main Content */}
      <div className="bg-white px-6 pb-6">
        {/* Goal Header */}
        <div className="pt-4 pb-6 border-b border-gray-100">
          <div className="flex items-center gap-3 mb-4">
            <div className={`w-12 h-12 ${iconColor.bg} rounded-xl flex items-center justify-center`}>
              <svg className={`w-6 h-6 ${iconColor.text}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            </div>
            <div className="flex-1">
              <h2 className="text-lg font-bold text-gray-900">{goal.name}</h2>
              <p className="text-xs text-gray-500">{goal.description}</p>
            </div>
            <span className={`px-3 py-1 ${getTypeBadge()} text-xs font-semibold rounded-full`}>
              {getTypeLabel()}
            </span>
          </div>

          {/* Progress Circle Large */}
          <div className="relative flex justify-center items-center h-48 mb-4">
            <svg className="w-full h-full max-w-[200px]" viewBox="0 0 200 200">
              <circle cx="100" cy="100" r={radius} fill="none" stroke="#E5E7EB" strokeWidth="8" />
              <circle
                cx="100"
                cy="100"
                r={radius}
                fill="none"
                stroke={strokeColor}
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                transform="rotate(-90 100 100)"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-4xl font-bold text-gray-900">{goal.percentage}%</span>
              <span className="text-xs text-gray-400 mt-1">usado</span>
            </div>
          </div>

          {/* Values */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-xs text-gray-500 mb-1">Gasto</p>
              <p className="text-base font-bold text-gray-900">R$ {goal.spent.toLocaleString('pt-BR')}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Orçamento</p>
              <p className="text-base font-bold text-gray-900">R$ {goal.budget.toLocaleString('pt-BR')}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Restante</p>
              <p className="text-base font-bold text-green-600">R$ {remaining.toLocaleString('pt-BR')}</p>
            </div>
          </div>
        </div>

        {/* Transactions History */}
        <div className="pt-6">
          <h3 className="text-sm font-bold text-gray-900 mb-4">Histórico de Gastos</h3>

          <div className="space-y-3">
            {mockTransactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-900">{transaction.description}</p>
                  <p className="text-xs text-gray-500">{new Date(transaction.date).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })}</p>
                </div>
                <span className="text-sm font-bold text-red-600">-R$ {transaction.amount.toLocaleString('pt-BR')}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="mt-6 px-6 grid grid-cols-2 gap-3">
        <button
          onClick={() => router.back()}
          className="bg-white text-gray-700 border border-gray-200 rounded-2xl py-4 font-bold hover:bg-gray-50 transition-all"
        >
          Voltar
        </button>
        <button
          onClick={handleEdit}
          className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl py-4 font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
        >
          Editar
        </button>
      </div>
    </div>
  );
}
