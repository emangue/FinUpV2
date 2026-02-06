interface IconButtonProps {
  onClick?: () => void;
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'danger';
}

export default function IconButton({ onClick, children, variant = 'default' }: IconButtonProps) {
  const variants = {
    default: 'text-gray-700 hover:text-gray-900',
    primary: 'text-blue-600 hover:text-blue-700',
    danger: 'text-red-600 hover:text-red-700'
  };

  return (
    <button 
      onClick={onClick}
      className={`${variants[variant]} transition-colors p-1`}
    >
      {children}
    </button>
  );
}
