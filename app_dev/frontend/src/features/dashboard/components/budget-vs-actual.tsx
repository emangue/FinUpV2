'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface BudgetData {
  categoria: string;
  realizado: number;
  planejado?: number;
  percentual: number;
}

interface BudgetVsActualProps {
  data?: BudgetData[];
  loading?: boolean;
  error?: string | null;
}

const BudgetVsActual: React.FC<BudgetVsActualProps> = ({
  data = [],
  loading = false,
  error = null
}) => {
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Despesas Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Carregando dados...</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Despesas Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <Badge variant="destructive" className="w-full justify-center py-4">
            Erro ao carregar dados: {error}
          </Badge>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Despesas Realizado vs Planejado</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-center py-8 text-gray-500">
          <div className="text-4xl mb-4">📊</div>
          <p>Apenas realizado disponível</p>
          <p className="text-sm mt-2">Planejamento será implementado em breve</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default BudgetVsActual;