/**
 * TabBar - Tabs de Tipo de Documento
 * Componente reutilizável para alternar entre Extrato e Fatura
 */

import { TabType } from '../types';

interface TabBarProps {
  activeTab: TabType;
  onChange: (tab: TabType) => void;
}

export function TabBar({ activeTab, onChange }: TabBarProps) {
  return (
    <div className="flex gap-3 mb-6">
      <button 
        onClick={() => onChange('extrato')}
        className={`flex-1 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
          activeTab === 'extrato'
            ? 'bg-gray-900 text-white shadow-lg'
            : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
        }`}
      >
        Extrato bancário
      </button>
      <button 
        onClick={() => onChange('fatura')}
        className={`flex-1 px-6 py-3 rounded-xl text-sm font-semibold transition-all ${
          activeTab === 'fatura'
            ? 'bg-gray-900 text-white shadow-lg'
            : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
        }`}
      >
        Fatura Cartão
      </button>
    </div>
  );
}
