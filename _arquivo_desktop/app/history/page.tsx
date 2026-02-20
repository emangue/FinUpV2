'use client';

import { MobileHistoryLayout } from '@/components/templates/MobileHistoryLayout';
import { WalletSummaryCard } from '@/components/organisms/WalletSummaryCard';
import { BottomNavigation } from '@/components/organisms/BottomNavigation';
import { MOCK_USER, MOCK_WALLET_DATA } from '@/lib/wallet-constants';

export default function HistoryPage() {
  return (
    <MobileHistoryLayout>
      <WalletSummaryCard
        user={MOCK_USER}
        walletData={MOCK_WALLET_DATA}
      />
      <BottomNavigation activeTab="home" />
    </MobileHistoryLayout>
  );
}
