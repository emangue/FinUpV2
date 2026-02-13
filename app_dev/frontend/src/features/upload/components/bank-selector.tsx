/**
 * BankSelector - Seletor de Instituição Financeira
 * Componente reutilizável para seleção de banco
 */

import { Bank } from '../types';

interface BankSelectorProps {
  banks: Bank[];
  value: string;
  onChange: (bankId: string) => void;
  required?: boolean;
}

export function BankSelector({ banks, value, onChange, required = false }: BankSelectorProps) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-bold text-gray-900 mb-2">
        Instituição Financeira {required && <span className="text-red-500">*</span>}
      </label>
      <div className="relative">
        <select 
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full px-4 py-3 border border-gray-200 rounded-xl text-gray-700 appearance-none cursor-pointer hover:border-gray-300 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
        >
          <option value="">Selecione o banco</option>
          {banks.map((bank) => {
            return (
              <option key={bank.id} value={bank.name}>
                {bank.name}
              </option>
            );
          })}
        </select>
        <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>
    </div>
  );
}
