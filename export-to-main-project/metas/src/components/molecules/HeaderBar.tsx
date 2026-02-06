'use client';

import IconButton from '../atoms/IconButton';

interface HeaderBarProps {
  title: string;
  onBack?: () => void;
  rightAction?: React.ReactNode;
}

export default function HeaderBar({ title, onBack, rightAction }: HeaderBarProps) {
  return (
    <header className="bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100">
      {onBack ? (
        <IconButton onClick={onBack}>
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
        </IconButton>
      ) : (
        <div className="w-6" />
      )}
      
      <h1 className="text-lg font-bold text-gray-800">{title}</h1>
      
      {rightAction || <div className="w-6" />}
    </header>
  );
}
