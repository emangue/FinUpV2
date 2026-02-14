// src/app/mobile/layout.tsx
// Mobile Experience V1.0 - Mobile Layout
// Data: 01/02/2026

import { BottomNavigation } from '@/components/mobile/bottom-navigation';

export default function MobileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-white pb-20">
      {/* pb-20 = espaço para bottom nav (80px) */}
      {children}
      <BottomNavigation />
    </div>
  );
}
