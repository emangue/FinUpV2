'use client';

import React from 'react';
import { Badge } from '@/components/ui/badge';

interface Metrics {
  totalDespesas: number;
  totalReceitas: number;
  saldoAtual: number;
  totalTransacoes: number;
}

interface SectionCardsProps {
  metrics?: Metrics;
  loading?: boolean;
  error?: string | null;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

const SectionCards: React.FC<SectionCardsProps> = ({ 
  metrics,
  loading = false,
  error = null
}) => {
  if (loading) {
    return (
      <div className="flex justify-between items-center mb-6">
        {Array.from({ length: 3 }, (_, i) => (
          <div key={i} className="text-center animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-20 mb-2 mx-auto"></div>
            <div className="h-8 bg-gray-200 rounded w-32 mx-auto"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="mb-6">
        <Badge variant="destructive" className="w-full justify-center py-2">
          Erro ao carregar dados: {error}
        </Badge>
      </div>
    );
  }

  if (!metrics) {
    return null;
  }

  const cards = [
    {
      icon: "💳",
      title: "Total Receitas", 
      value: formatCurrency(metrics.totalReceitas),
      className: "text-green-600",
    },
    {
      icon: "📊",
      title: "Total Despesas",
      value: formatCurrency(metrics.totalDespesas),
      className: "text-red-600",
    },
    {
      icon: "💰",
      title: "Saldo Atual",
      value: formatCurrency(metrics.saldoAtual),
      className: metrics.saldoAtual >= 0 ? "text-green-600" : "text-red-600",
    },
  ];

  return (
    <div className="flex justify-between items-center mb-6">
      {cards.map((card, index) => (
        <div key={index} className="text-center">
          <div className="flex items-center justify-center gap-2 mb-1">
            <span className="text-lg">{card.icon}</span>
            <span className="text-sm text-gray-600">{card.title}</span>
          </div>
          <div className={`text-2xl font-bold ${card.className}`}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SectionCards;