interface MonthButtonProps {
  label: string;
  year: string;
  active: boolean;
  onClick: () => void;
}

export default function MonthButton({ label, year, active, onClick }: MonthButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`px-6 py-3 rounded-2xl font-semibold text-sm transition-all flex-shrink-0 ${
        active
          ? 'bg-blue-500 text-white shadow-md scale-105'
          : 'bg-white text-gray-400 hover:bg-gray-50'
      }`}
    >
      <div className="text-center">
        <div className="text-base font-bold">{label}</div>
        <div className="text-xs opacity-75">{year}</div>
      </div>
    </button>
  );
}
