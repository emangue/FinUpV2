interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'info';
  className?: string;
}

export default function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 text-gray-700',
    success: 'bg-green-100 text-green-700',
    warning: 'bg-orange-100 text-orange-700',
    info: 'bg-blue-100 text-blue-700',
  };

  return (
    <span
      className={`inline-block px-2 py-0.5 text-xs font-semibold rounded-md ${variants[variant]} ${className}`}
    >
      {children}
    </span>
  );
}
