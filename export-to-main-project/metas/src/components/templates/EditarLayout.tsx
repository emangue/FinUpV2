'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { mockGoals } from '@/lib/constants';

export default function EditarLayout() {
  const router = useRouter();
  const goal = mockGoals[0]; // Mock - primeira meta

  const [type, setType] = useState(goal.type);
  const [name, setName] = useState(goal.name);
  const [description, setDescription] = useState(goal.description || '');
  const [budget, setBudget] = useState(goal.budget);
  const [selectedIcon, setSelectedIcon] = useState(0);
  const [alertAt80, setAlertAt80] = useState(goal.alertAt80);
  const [alertAt100, setAlertAt100] = useState(goal.alertAt100);
  const [applyFutureMonths, setApplyFutureMonths] = useState(false);

  const icons = [
    { svg: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6', color: 'blue' },
    { svg: 'M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z', color: 'green' },
    { svg: 'M12 6v6m0 0v6m0-6h6m-6 0H6', color: 'orange' },
    { svg: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z', color: 'pink' }
  ];

  const getIconClasses = (index: number) => {
    if (selectedIcon === index) {
      return `bg-${icons[index].color}-100 border-${icons[index].color}-500 text-${icons[index].color}-600`;
    }
    return 'bg-gray-100 border-gray-200 text-gray-400';
  };

  const handleSave = () => {
    alert('Meta salva!');
    router.back();
  };

  const handleDelete = () => {
    if (confirm('Deseja realmente excluir esta meta?')) {
      router.push('/');
    }
  };

  return (
    <div className="w-full max-w-md mx-auto animate-fade-in">
      {/* Header */}
      <header className="bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100">
        <button onClick={() => router.back()} className="text-gray-700 hover:text-gray-900 transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <h1 className="text-lg font-bold text-gray-800">Editar Meta</h1>
        <button onClick={handleSave} className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors">
          Salvar
        </button>
      </header>

      {/* Date */}
      <div className="bg-white px-6 py-2">
        <p className="text-xs text-gray-400 text-right">Fevereiro 2026</p>
      </div>

      {/* Main Content */}
      <div className="bg-white px-6 pb-6 rounded-b-3xl">
        <div className="pt-4 space-y-5">
          {/* Tipo de Meta */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2">Tipo de Meta</label>
            <div className="flex gap-3">
              <button
                onClick={() => setType('gasto')}
                className={`flex-1 py-3 px-4 border-2 rounded-xl font-semibold text-sm transition-all ${
                  type === 'gasto'
                    ? 'bg-orange-50 border-orange-500 text-orange-700'
                    : 'bg-white border-gray-200 text-gray-400 hover:border-orange-500 hover:text-orange-700 hover:bg-orange-50'
                }`}
              >
                Gasto
              </button>
              <button
                onClick={() => setType('investimento')}
                className={`flex-1 py-3 px-4 border-2 rounded-xl font-semibold text-sm transition-all ${
                  type === 'investimento'
                    ? 'bg-purple-50 border-purple-500 text-purple-700'
                    : 'bg-white border-gray-200 text-gray-400 hover:border-purple-500 hover:text-purple-700 hover:bg-purple-50'
                }`}
              >
                Investimento
              </button>
            </div>
          </div>

          {/* Nome */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2">Nome</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Descrição */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2">Descrição</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Orçamento */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2">Orçamento Mensal</label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-semibold">R$</span>
              <input
                type="number"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Categoria/Ícone */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-2">Categoria</label>
            <div className="grid grid-cols-4 gap-3">
              {icons.map((icon, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedIcon(index)}
                  className={`aspect-square border-2 rounded-xl flex items-center justify-center hover:scale-105 transition-all ${
                    selectedIcon === index
                      ? `bg-${icon.color}-100 border-${icon.color}-500`
                      : 'bg-gray-100 border-gray-200 hover:border-gray-400'
                  }`}
                >
                  <svg
                    className={`w-6 h-6 ${
                      selectedIcon === index ? `text-${icon.color}-600` : 'text-gray-400'
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon.svg} />
                  </svg>
                </button>
              ))}
            </div>
          </div>

          {/* Alertas */}
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-3">Alertas</label>
            <div className="space-y-3">
              <label className="flex items-center justify-between p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors">
                <span className="text-sm text-gray-700">Alertar ao atingir 80%</span>
                <input
                  type="checkbox"
                  checked={alertAt80}
                  onChange={(e) => setAlertAt80(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
              </label>
              <label className="flex items-center justify-between p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors">
                <span className="text-sm text-gray-700">Alertar ao atingir 100%</span>
                <input
                  type="checkbox"
                  checked={alertAt100}
                  onChange={(e) => setAlertAt100(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
              </label>
            </div>
          </div>

          {/* Aplicar para Meses Futuros */}
          <div className="pt-2">
            <div className="border-t border-gray-200 pt-4">
              <label className="block text-xs font-semibold text-gray-700 mb-3">Recorrência</label>
              <label className="flex items-center justify-between p-4 bg-blue-50 border-2 border-blue-200 rounded-xl cursor-pointer hover:bg-blue-100 transition-colors">
                <div className="flex-1">
                  <div className="text-sm font-semibold text-gray-900">Aplicar para meses posteriores</div>
                  <div className="text-xs text-gray-500 mt-1">
                    As alterações serão aplicadas de março a dezembro de 2026
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={applyFutureMonths}
                  onChange={(e) => setApplyFutureMonths(e.target.checked)}
                  className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                />
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="mt-6 px-6 space-y-3">
        <button
          onClick={handleSave}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl py-4 font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
        >
          Salvar Alterações
        </button>
        <button
          onClick={handleDelete}
          className="w-full bg-white text-red-600 border border-red-200 rounded-2xl py-4 font-bold hover:bg-red-50 transition-all"
        >
          Excluir Meta
        </button>
      </div>
    </div>
  );
}
