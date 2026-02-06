'use client';

import { useState } from 'react';
import { Goal, GoalType } from '@/types';
import GoalIcon from '../atoms/GoalIcon';

interface GoalEditFormProps {
  goal?: Goal;
  onSave: (data: Partial<Goal>) => void;
  onDelete?: () => void;
}

export default function GoalEditForm({ goal, onSave, onDelete }: GoalEditFormProps) {
  const [type, setType] = useState<GoalType>(goal?.type || 'gasto');
  const [name, setName] = useState(goal?.name || '');
  const [description, setDescription] = useState(goal?.description || '');
  const [budget, setBudget] = useState(goal?.budget || 0);
  const [selectedIcon, setSelectedIcon] = useState(goal?.icon || 'home');
  const [selectedColor, setSelectedColor] = useState(goal?.color || 'blue');
  const [alertAt80, setAlertAt80] = useState(goal?.alertAt80 ?? true);
  const [alertAt100, setAlertAt100] = useState(goal?.alertAt100 ?? true);
  const [applyFutureMonths, setApplyFutureMonths] = useState(false);

  const icons = ['home', 'shopping', 'plus', 'heart', 'globe'];
  const colors = ['blue', 'green', 'orange', 'pink', 'purple'];

  const handleSubmit = () => {
    onSave({
      type,
      name,
      description,
      budget,
      icon: selectedIcon,
      color: selectedColor,
      alertAt80,
      alertAt100
    });
  };

  return (
    <div className="space-y-6">
      {/* Type Selection */}
      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-2">Tipo</label>
        <div className="flex gap-3">
          <button
            onClick={() => setType('gasto')}
            className={`flex-1 py-3 rounded-xl font-semibold text-sm transition-all ${
              type === 'gasto'
                ? 'bg-blue-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Gasto Mensal
          </button>
          <button
            onClick={() => setType('investimento')}
            className={`flex-1 py-3 rounded-xl font-semibold text-sm transition-all ${
              type === 'investimento'
                ? 'bg-purple-500 text-white shadow-md'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            Investimento
          </button>
        </div>
      </div>

      {/* Name */}
      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-2">Nome da Meta</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Ex: Casa, Transporte..."
          className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Description */}
      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-2">Descrição (opcional)</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Adicione uma descrição..."
          rows={3}
          className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
        />
      </div>

      {/* Budget */}
      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-2">
          {type === 'gasto' ? 'Orçamento Mensal' : 'Valor Total'}
        </label>
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

      {/* Icon and Color Selection */}
      <div>
        <label className="block text-xs font-semibold text-gray-700 mb-2">Ícone e Cor</label>
        <div className="grid grid-cols-5 gap-3">
          {icons.map((icon) => (
            <button
              key={icon}
              onClick={() => setSelectedIcon(icon)}
              className={`aspect-square rounded-xl flex items-center justify-center transition-all ${
                selectedIcon === icon
                  ? 'ring-2 ring-blue-500 scale-105'
                  : 'hover:scale-105'
              }`}
            >
              <GoalIcon icon={icon} color={selectedColor} />
            </button>
          ))}
        </div>
        <div className="grid grid-cols-5 gap-3 mt-3">
          {colors.map((color) => (
            <button
              key={color}
              onClick={() => setSelectedColor(color)}
              className={`aspect-square rounded-xl transition-all ${
                selectedColor === color
                  ? 'ring-2 ring-offset-2 ring-blue-500 scale-105'
                  : 'hover:scale-105'
              } ${getColorClass(color)}`}
            />
          ))}
        </div>
      </div>

      {/* Alerts */}
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

      {/* Apply to Future Months */}
      <div className="pt-2 border-t border-gray-200">
        <label className="block text-xs font-semibold text-gray-700 mb-3">Recorrência</label>
        <label className="flex items-center justify-between p-4 bg-blue-50 border-2 border-blue-200 rounded-xl cursor-pointer hover:bg-blue-100 transition-colors">
          <div className="flex-1">
            <div className="text-sm font-semibold text-gray-900">Aplicar para meses posteriores</div>
            <div className="text-xs text-gray-500 mt-1">As alterações serão aplicadas de março a dezembro de 2026</div>
          </div>
          <input
            type="checkbox"
            checked={applyFutureMonths}
            onChange={(e) => setApplyFutureMonths(e.target.checked)}
            className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
          />
        </label>
      </div>

      {/* Action Buttons */}
      <div className="space-y-3 pt-4">
        <button
          onClick={handleSubmit}
          className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl py-4 font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
        >
          Salvar Alterações
        </button>
        {onDelete && (
          <button
            onClick={onDelete}
            className="w-full bg-white text-red-600 border border-red-200 rounded-2xl py-4 font-bold hover:bg-red-50 transition-all"
          >
            Excluir Meta
          </button>
        )}
      </div>
    </div>
  );
}

function getColorClass(color: string): string {
  const classes: Record<string, string> = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    orange: 'bg-orange-500',
    pink: 'bg-pink-500',
    purple: 'bg-purple-500'
  };
  return classes[color] || classes.blue;
}
