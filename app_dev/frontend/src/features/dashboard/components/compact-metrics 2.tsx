'use client';

import React from 'react';

interface Metrics {
  totalDespesas: number;
  totalReceitas: number;
  saldoAtual: number;
  totalTransacoes: number;
}

interface CompactMetricsProps {
  metrics?: Metrics;
  loading?: boolean;
  error?: string | null;
}

const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

const CompactMetrics: React.FC<CompactMetricsProps> = ({ 
  metrics,
  loading = false,
  error = null
}) => {
  if (loading) {
    return (
      <div className="flex gap-6 text-sm">
        <div className="animate-pulse">
          <div className="h-3 bg-gray-200 rounded w-16 mb-1"></div>
          <div className="h-4 bg-gray-200 rounded w-20"></div>
        </div>
        <div className="animate-pulse">
          <div className="h-3 bg-gray-200 rounded w-16 mb-1"></div>
          <div className="h-4 bg-gray-200 rounded w-20"></div>
        </div>
        <div className="animate-pulse">
          <div className="h-3 bg-gray-200 rounded w-16 mb-1"></div>
          <div className="h-4 bg-gray-200 rounded w-20"></div>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return null;
  }

  return (
    <div className="flex gap-6 text-sm">
      <div>
        <div className="text-xs text-gray-500 mb-1">Receitas</div>
        <div className="font-semibold text-green-600">
          {formatCurrency(metrics.totalReceitas)}
        </div>
      </div>
      <div>
        <div className="text-xs text-gray-500 mb-1">Despesas</div>
        <div className="font-semibold text-red-600">
          {formatCurrency(metrics.totalDespesas)}
        </div>
      </div>
      <div>
        <div className="text-xs text-gray-500 mb-1">Saldo</div>
        <div className={`font-semibold ${metrics.saldoAtual >= 0 ? 'text-green-600' : 'text-red-600'}`}>
          {formatCurrency(metrics.saldoAtual)}
        </div>
      </div>
    </div>
  );
};

export default CompactMetrics;