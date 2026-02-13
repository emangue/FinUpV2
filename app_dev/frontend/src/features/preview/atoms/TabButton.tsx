interface TabButtonProps {
  label: string;
  count: number;
  active?: boolean;
  variant?: 'default' | 'warning';
  onClick?: () => void;
}

export default function TabButton({ 
  label, 
  count, 
  active = false, 
  variant = 'default',
  onClick 
}: TabButtonProps) {
  const baseClasses = 'px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-all';
  
  const variantClasses = {
    default: active 
      ? 'bg-gray-900 text-white' 
      : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    warning: active
      ? 'bg-orange-600 text-white'
      : 'bg-orange-100 text-orange-700 hover:bg-orange-200',
  };

  return (
    <button 
      onClick={onClick}
      className={`${baseClasses} ${variantClasses[variant]}`}
    >
      {label} ({count})
    </button>
  );
}
