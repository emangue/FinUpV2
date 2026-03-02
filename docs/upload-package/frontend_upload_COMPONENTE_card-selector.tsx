/**
 * CardSelector - Seletor de Cartão de Crédito
 * Componente reutilizável para seleção de cartão com botão de adicionar
 */

import { CreditCard } from '../types';

interface CardSelectorProps {
  cards: CreditCard[];
  value: string;
  onChange: (cardId: string) => void;
  onAddNew?: () => void;
  required?: boolean;
}

export function CardSelector({ cards, value, onChange, onAddNew, required = false }: CardSelectorProps) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-bold text-gray-900 mb-2">
        Cartão de Crédito {required && <span className="text-red-500">*</span>}
      </label>
      <div className="flex gap-3">
        <div className="relative flex-1">
          <select 
            value={value}
            onChange={(e) => onChange(e.target.value)}
            className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          >
            <option value="">Selecione o cartão</option>
            {cards.map((card) => (
              <option key={card.id} value={card.id}>{card.name}</option>
            ))}
          </select>
          <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </div>
        {onAddNew && (
          <button 
            onClick={onAddNew}
            className="w-12 h-12 flex items-center justify-center bg-gray-50 hover:bg-gray-100 rounded-xl transition-colors"
            aria-label="Adicionar novo cartão"
          >
            <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
