interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'disabled';
  fullWidth?: boolean;
  type?: 'button' | 'submit';
  className?: string;
}

export default function Button({
  children,
  onClick,
  variant = 'primary',
  fullWidth = false,
  type = 'button',
  className = '',
}: ButtonProps) {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95',
    secondary: 'bg-gray-200 text-gray-700 hover:bg-gray-300',
    disabled: 'bg-gray-300 text-gray-500 cursor-not-allowed',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={variant === 'disabled'}
      className={`
        ${variants[variant]}
        ${fullWidth ? 'w-full' : ''}
        px-4 py-2.5 rounded-lg font-semibold text-sm
        transition-all shadow-sm
        ${className}
      `}
    >
      {children}
    </button>
  );
}
