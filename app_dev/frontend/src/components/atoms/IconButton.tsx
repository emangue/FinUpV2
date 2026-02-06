import { LucideIcon } from 'lucide-react';

interface IconButtonProps {
  icon: LucideIcon;
  label: string;
  isActive?: boolean;
  onClick?: () => void;
}

export function IconButton({
  icon: Icon,
  label,
  isActive = false,
  onClick
}: IconButtonProps) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className={`
        flex items-center justify-center
        w-12 h-12 rounded-full
        transition-colors duration-200
        ${isActive 
          ? 'bg-blue-500 text-white' 
          : 'text-gray-400 hover:text-gray-600'
        }
      `}
    >
      <Icon size={24} />
    </button>
  );
}
