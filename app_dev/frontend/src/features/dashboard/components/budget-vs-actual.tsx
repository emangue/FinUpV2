'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { DemaisBreakdownModal } from './demais-breakdown-modal';
import { TipoGastoBreakdownModal } from './tipo-gasto-breakdown-modal';

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
  const [demaisModalOpen, setDemaisModalOpen] = useState(false);
  const [demaisTipos, setDemaisTipos] = useState<BudgetVsActualItem[]>([]);
  const [tipoGastoModalOpen, setTipoGastoModalOpen] = useState(false);
  const [selectedTipoGasto, setSelectedTipoGasto] = useState<string>('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setFetchError(null);

        // Se month='all', buscar YTD (Year to Date)
        const url = month === 'all' 
          ? `/api/dashboard/budget-vs-actual?year=${year}&ytd=true`
          : `/api/dashboard/budget-vs-actual?year=${year}&month=${month}`;
        
        const response = await fetch(url);

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
        {/* Layout: Barras à esquerda, Gráfico circular + Totais à direita */}
        <div className="grid grid-cols-2 gap-6">
          {/* Coluna Esquerda - Lista de categorias (top 5 + Demais) */}
          <div className="space-y-4">
            {(() => {
              // Verificar se há algum planejado > 0
              const temPlanejado = data.items.some(item => item.planejado > 0);
              
              // Ordenar por planejado (se houver) ou por realizado
              const sortedItems = [...data.items].sort((a, b) => {
                if (temPlanejado) {
                  return b.planejado - a.planejado;
                } else {
                  return b.realizado - a.realizado;
                }
              });
              
              // Pegar top 5
              const top5 = sortedItems.slice(0, 5);
              
              // Agrupar os demais
              const others = sortedItems.slice(5);
              const demaisItem = others.length > 0 ? {
                tipo_gasto: 'Demais',
                realizado: others.reduce((sum, item) => sum + item.realizado, 0),
                planejado: others.reduce((sum, item) => sum + item.planejado, 0),
                percentual: 0, // Será calculado abaixo
                diferenca: 0,
                tipos_inclusos: others // Lista completa de items no "Demais"
              } : null;
              
              // Calcular percentual para "Demais"
              if (demaisItem) {
                demaisItem.percentual = demaisItem.planejado > 0 
                  ? (demaisItem.realizado / demaisItem.planejado) * 100 
                  : 0;
                demaisItem.diferenca = demaisItem.realizado - demaisItem.planejado;
              }
              
              // Combinar top 5 + Demais
              const displayItems = demaisItem ? [...top5, demaisItem] : top5;
              
              return displayItems.map((item) => {
                // Se for "Demais", abrir modal em vez de link direto
                const isDemais = item.tipo_gasto === 'Demais' && 'tipos_inclusos' in item;
                
                const handleClick = (e: React.MouseEvent) => {
                  if (isDemais) {
                    e.preventDefault();
                    setDemaisTipos(item.tipos_inclusos);
                    setDemaisModalOpen(true);
                  } else {
                    // Abrir modal de subgrupos para tipo de gasto normal
                    e.preventDefault();
                    setSelectedTipoGasto(item.tipo_gasto);
                    setTipoGastoModalOpen(true);
                  }
                };
                
                return (
                <div key={item.tipo_gasto} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium truncate">{item.tipo_gasto}</span>
                    <div className="flex items-center gap-2">
                      <span className={`font-bold ${getColorClass(item.percentual)}`}>
                        {item.percentual.toFixed(1)}%
                      </span>
                      <button
                        onClick={handleClick}
                        className="text-muted-foreground text-xs hover:text-primary hover:underline cursor-pointer"
                      >
                        {formatCurrency(item.realizado)}
                      </button>
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
              )});
            })()}
          </div>

          {/* Coluna Direita - Gráfico circular + Totais */}
          <div className="flex flex-col items-center justify-center space-y-6">
            {/* Gráfico circular */}
            <div className="relative w-48 h-48">
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
                <span className="text-4xl font-bold text-black">
                  {Math.round(data.percentual_geral)}%
                </span>
              </div>
            </div>

            {/* Totais */}
            <div className="w-full space-y-2 text-sm">
              <div className="flex justify-between font-medium">
                <span>Total Realizado:</span>
                <span>{formatCurrency(data.total_realizado)}</span>
              </div>
              <div className="flex justify-between font-medium">
                <span>Total Planejado:</span>
                <span>{formatCurrency(data.total_planejado)}</span>
              </div>
              <div className="flex justify-between font-bold pt-2 border-t">
                <span>Diferença:</span>
                <span className={data.total_realizado > data.total_planejado ? 'text-red-600' : 'text-green-600'}>
                  {formatCurrency(data.total_realizado - data.total_planejado)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>

      {/* Modal de detalhamento do "Demais" */}
      <DemaisBreakdownModal
        open={demaisModalOpen}
        onOpenChange={setDemaisModalOpen}
        tipos={demaisTipos}
        year={parseInt(year)}
        month={parseInt(month)}
      />

      {/* Modal de detalhamento de Tipo de Gasto (subgrupos) */}
      <TipoGastoBreakdownModal
        open={tipoGastoModalOpen}
        onOpenChange={setTipoGastoModalOpen}
        tipoGasto={selectedTipoGasto}
        year={parseInt(year)}
        month={month === 'all' ? 0 : parseInt(month)}
      />
    </Card>
  );
}
