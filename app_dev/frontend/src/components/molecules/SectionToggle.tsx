interface SectionToggleProps {
  activeTab: 'month' | 'ytd';
  onToggle: (tab: 'month' | 'ytd') => void;
}

export function SectionToggle({ activeTab, onToggle }: SectionToggleProps) {
  return (
    <div className="flex gap-2 bg-gray-100 rounded-xl p-1">
      <button
        onClick={() => onToggle('month')}
        className={`flex-1 py-2 px-4 rounded-lg text-sm font-semibold transition-all ${
          activeTab === 'month'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        Mês
      </button>
      <button
        onClick={() => onToggle('ytd')}
        className={`flex-1 py-2 px-4 rounded-lg text-sm font-semibold transition-all ${
          activeTab === 'ytd'
            ? 'bg-white text-gray-900 shadow-sm'
            : 'text-gray-500 hover:text-gray-700'
        }`}
      >
        YTD
      </button>
    </div>
  );
}
