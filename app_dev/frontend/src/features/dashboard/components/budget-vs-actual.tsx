'use client';

import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';

interface BudgetVsActualItem {
  tipo_gasto: string;
  realizado: number;
  planejado: number;
  percentual: number;
  diferenca: number;
}

interface BudgetVsActualData {
  items: BudgetVsActualItem[];
  total_realizado: number;
  total_planejado: number;
  percentual_geral: number;
}

interface BudgetVsActualProps {
  year: string;
  month: string;
  loading?: boolean;
  error?: string | null;
}

export function BudgetVsActual({ year, month, loading = false, error = null }: BudgetVsActualProps) {
  const [data, setData] = useState<BudgetVsActualData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // Se month='all', não buscar (budget-vs-actual requer mês específico)
      if (month === 'all') {
        setData(null);
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setFetchError(null);

        const response = await fetch(
          `/api/dashboard/budget-vs-actual?year=${year}&month=${month}`
        );

        if (!response.ok) {
          throw new Error(`Erro ao buscar budget vs actual: ${response.statusText}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        console.error('Error fetching budget vs actual:', err);
        setFetchError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [year, month]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const getColorClass = (percentual: number) => {
    if (percentual < 80) return 'text-green-600';
    if (percentual < 100) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (percentual: number) => {
    if (percentual < 80) return 'bg-green-500';
    if (percentual < 100) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading || isLoading) {
    return (
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle className="text-lg">Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="animate-pulse text-muted-foreground">
              Carregando...
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || fetchError) {
    return (
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle className="text-lg">Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-destructive">
            <AlertCircle className="mr-2 h-4 w-4" />
            {error || fetchError}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (month === 'all') {
    return (
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle className="text-lg">Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            Selecione um mês específico para ver o orçamento
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <Card className="col-span-1">
        <CardHeader>
          <CardTitle className="text-lg">Realizado vs Planejado</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
            <p>Nenhum orçamento definido para este mês</p>
            <p className="text-sm mt-2">Configure seu orçamento na página de Planejamento</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle className="text-lg">Realizado vs Planejado</CardTitle>
      </CardHeader>
      <CardContent>
        {/* Gráfico circular com percentual geral */}
        <div className="flex justify-center mb-6">
          <div className="relative w-32 h-32">
            {/* SVG Donut Chart */}
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
              {/* Background circle */}
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke="#e5e7eb"
                strokeWidth="12"
              />
              {/* Progress circle */}
              <circle
                cx="60"
                cy="60"
                r="50"
                fill="none"
                stroke={data.percentual_geral >= 100 ? '#ef4444' : '#f97316'}
                strokeWidth="12"
                strokeDasharray={`${(data.percentual_geral / 100) * 314} 314`}
                strokeLinecap="round"
              />
            </svg>
            {/* Percentual no centro */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className={`text-2xl font-bold ${getColorClass(data.percentual_geral)}`}>
                {Math.round(data.percentual_geral)}%
              </span>
            </div>
          </div>
        </div>

        {/* Lista de categorias */}
        <div className="space-y-4">
          {data.items.map((item) => (
            <div key={item.tipo_gasto} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">{item.tipo_gasto}</span>
                <div className="flex items-center gap-2">
                  <span className={`font-bold ${getColorClass(item.percentual)}`}>
                    {item.percentual.toFixed(1)}%
                  </span>
                  <span className="text-muted-foreground">
                    {formatCurrency(item.realizado)}
                  </span>
                </div>
              </div>
              <Progress 
                value={Math.min(item.percentual, 100)} 
                className="h-2"
                indicatorClassName={getProgressColor(item.percentual)}
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>Planejado: {formatCurrency(item.planejado)}</span>
                {item.diferenca !== 0 && (
                  <span className={`flex items-center gap-1 ${item.diferenca > 0 ? 'text-red-500' : 'text-green-500'}`}>
                    {item.diferenca > 0 ? (
                      <>
                        <TrendingUp className="h-3 w-3" />
                        +{formatCurrency(Math.abs(item.diferenca))}
                      </>
                    ) : (
                      <>
                        <TrendingDown className="h-3 w-3" />
                        {formatCurrency(Math.abs(item.diferenca))}
                      </>
                    )}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Totais */}
        <div className="mt-6 pt-4 border-t space-y-2">
          <div className="flex justify-between text-sm font-medium">
            <span>Total Realizado:</span>
            <span>{formatCurrency(data.total_realizado)}</span>
          </div>
          <div className="flex justify-between text-sm font-medium">
            <span>Total Planejado:</span>
            <span>{formatCurrency(data.total_planejado)}</span>
          </div>
          <div className="flex justify-between text-sm font-bold">
            <span>Diferença:</span>
            <span className={data.total_realizado > data.total_planejado ? 'text-red-600' : 'text-green-600'}>
              {formatCurrency(data.total_realizado - data.total_planejado)}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
