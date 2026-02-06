interface TabButtonProps {
  label: string;
  active: boolean;
  onClick: () => void;
  count?: number;
}

export default function TabButton({ label, active, onClick, count }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition-all ${
        active
          ? 'bg-blue-500 text-white shadow-md'
          : 'bg-white text-gray-500 hover:bg-gray-50'
      }`}
    >
      {label}
      {count !== undefined && (
        <span className={`ml-2 ${active ? 'opacity-80' : 'opacity-60'}`}>
          ({count})
        </span>
      )}
    </button>
  );
}
