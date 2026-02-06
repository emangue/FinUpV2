// src/components/mobile/icon-button.tsx
// Mobile Experience V1.0 - IconButton Component
// Data: 01/02/2026

'use client';

import { cn } from '@/lib/utils';
import { mobileAnimations } from '@/config/mobile-animations';

interface IconButtonProps {
  icon: React.ReactNode;
  label: string; // aria-label
  onClick: () => void;
  variant?: 'default' | 'primary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}

export function IconButton({
  icon,
  label,
  onClick,
  variant = 'default',
  size = 'md',
  disabled = false,
  className,
}: IconButtonProps) {
  const variantStyles = {
    default: 'bg-gray-100 text-gray-700 hover:bg-gray-200',
    primary: 'bg-black text-white hover:bg-gray-800',
    danger: 'bg-red-100 text-red-700 hover:bg-red-200',
  };

  const sizeStyles = {
    sm: 'w-9 h-9', // 36px
    md: 'w-11 h-11', // 44px (WCAG minimum)
    lg: 'w-14 h-14', // 56px (FABs)
  };

  const iconSizeStyles = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      aria-label={label}
      className={cn(
        'rounded-full flex items-center justify-center',
        variantStyles[variant],
        sizeStyles[size],
        mobileAnimations.button.tailwind,
        disabled && 'opacity-50 cursor-not-allowed',
        className
      )}
    >
      <span className={iconSizeStyles[size]}>{icon}</span>
    </button>
  );
}
