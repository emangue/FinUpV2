// src/components/mobile/mobile-header.tsx
// Mobile Experience V1.0 - MobileHeader Component
// Data: 01/02/2026

'use client';

import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { IconButton } from './icon-button';
import { mobileTypography } from '@/config/mobile-typography';
import { cn } from '@/lib/utils';

interface Action {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
}

interface MobileHeaderProps {
  title: string;
  subtitle?: string;
  leftAction?: 'back' | 'logo' | null;
  rightActions?: Action[];
  onBack?: () => void;
  variant?: 'default' | 'centered';
}

export function MobileHeader({
  title,
  subtitle,
  leftAction = null,
  rightActions = [],
  onBack,
  variant = 'default',
}: MobileHeaderProps) {
  const router = useRouter();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      router.back();
    }
  };

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between h-14 px-4">
        {/* Left Section */}
        <div className="flex items-center gap-3 flex-1">
          {leftAction === 'back' && (
            <IconButton
              icon={<ArrowLeft className="w-5 h-5" />}
              label="Voltar"
              onClick={handleBack}
            />
          )}
          
          {leftAction === 'logo' && (
            <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">F</span>
            </div>
          )}
          
          {variant === 'default' && leftAction !== null && (
            <div className="flex-1">
              <h1 className={cn(mobileTypography.categoryName.tailwind, 'text-[20px]')}>
                {title}
              </h1>
              {subtitle && (
                <p className={mobileTypography.frequency.tailwind}>{subtitle}</p>
              )}
            </div>
          )}
        </div>

        {/* Center Section (for centered variant) */}
        {variant === 'centered' && (
          <div className="absolute left-1/2 transform -translate-x-1/2">
            <h1 className={cn(mobileTypography.categoryName.tailwind, 'text-[20px]')}>
              {title}
            </h1>
          </div>
        )}

        {/* Right Actions */}
        <div className="flex items-center gap-2">
          {rightActions.map((action, index) => (
            <IconButton
              key={index}
              icon={action.icon}
              label={action.label}
              onClick={action.onClick}
            />
          ))}
        </div>
      </div>
    </header>
  );
}
