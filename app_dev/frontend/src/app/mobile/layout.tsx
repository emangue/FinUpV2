// src/app/mobile/layout.tsx
// Mobile Experience V1.0 - Mobile Layout
// Data: 01/02/2026
// Onboarding: sem bottom nav em /mobile/onboarding/*

'use client';

import { usePathname } from 'next/navigation';
import { BottomNavigation } from '@/components/mobile/bottom-navigation';
import { OnboardingGuard } from '@/features/onboarding/OnboardingGuard';
import { PendingUploadProvider } from '@/contexts/PendingUploadContext';

export default function MobileLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isOnboarding = pathname?.startsWith('/mobile/onboarding');

  return (
    <OnboardingGuard>
      <PendingUploadProvider>
        <div className={`min-h-screen bg-white ${isOnboarding ? '' : 'pb-20'}`}>
          {children}
          {!isOnboarding && <BottomNavigation />}
        </div>
      </PendingUploadProvider>
    </OnboardingGuard>
  );
}
