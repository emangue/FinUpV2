import { ReactNode } from 'react';

interface MobileHistoryLayoutProps {
  children: ReactNode;
}

export function MobileHistoryLayout({ children }: MobileHistoryLayoutProps) {
  return (
    <div className="min-h-screen bg-[#F7F8FA]">
      <div className="max-w-md mx-auto px-4 py-6">
        {children}
      </div>
    </div>
  );
}
