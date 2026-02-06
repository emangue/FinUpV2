'use client';

import { useState } from 'react';
import { StatCard } from '@/components/molecules/StatCard';
import { HeaderBar } from '@/components/molecules/HeaderBar';
import { SectionToggle } from '@/components/molecules/SectionToggle';
import { DonutChart } from './DonutChart';
import { CategoryList } from './CategoryList';
import { User, WalletData } from '@/types/wallet';

interface WalletSummaryCardProps {
  user: User;
  walletData: WalletData;
}

export function WalletSummaryCard({ user, walletData }: WalletSummaryCardProps) {
  const [activeTab, setActiveTab] = useState<'month' | 'ytd'>('month');
  
  // Calcular soma total dos valores
  const totalValue = walletData.categories.reduce((sum, cat) => sum + cat.value, 0);
  
  // Por enquanto, mês e YTD mostram os mesmos dados (será conectado ao backend depois)
  const displayCategories = walletData.categories;
  
  // Preparar dados do donut chart
  const donutData = walletData.categories.map(cat => ({
    label: cat.label,
    value: (walletData.total * cat.percentage) / 100,
    color: cat.color,
    percentage: cat.percentage
  }));
  
  return (
    <div className="pb-24"> {/* Espaço para bottom nav */}
      <StatCard padding="p-6">
        {/* Header */}
        <HeaderBar
          title="History"
          avatarSrc={user.avatar}
          selectedMonth={walletData.month}
        />
        
        {/* Gráfico Donut */}
        <DonutChart
          data={donutData}
          centerText={{
            title: new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
              minimumFractionDigits: 2
            }).format(totalValue),
            subtitle: walletData.month,
            caption: `Total ${activeTab === 'month' ? 'do mês' : 'YTD'}`
          }}
        />
        
        {/* Toggle Mês / YTD */}
        <div className="mt-6">
          <SectionToggle activeTab={activeTab} onToggle={setActiveTab} />
        </div>
        
        {/* Lista de Categorias */}
        <div className="mt-4">
          <CategoryList title="" categories={displayCategories} />
        </div>
      </StatCard>
    </div>
  );
}
