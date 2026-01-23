'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown, Activity, ChevronDown, ChevronUp, Upload } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useRouter } from 'next/navigation'
import ChartAreaInteractive from '../chart-area-interactive'

interface Metrics {
  totalDespesas: number
  totalReceitas: number
  saldoAtual: number
  totalTransacoes: number
}

interface ChartDataItem {
  mes: string
  receitas: number
  despesas: number
}

interface MetricCardsProps {
  metrics: Metrics | null
  loading: boolean
  error: string | null
  chartData: ChartDataItem[]
  chartLoading: boolean
  chartError: string | null
  selectedMonth: string
  onChartMonthClick: (month: string) => void
}

export function MetricCards({ 
  metrics, 
  loading, 
  error,
  chartData,
  chartLoading,
  chartError,
  selectedMonth,
  onChartMonthClick 
}: MetricCardsProps) {
  const [isChartExpanded, setIsChartExpanded] = useState(false)
  const router = useRouter()
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  if (loading) {
    return (
      <div className="space-y-3">
        {/* Skeleton do card grande */}
        <div className="h-32 bg-gray-200 animate-pulse rounded-2xl" />
        {/* Skeleton dos cards pequenos */}
        <div className="grid grid-cols-2 gap-3">
          <div className="h-24 bg-gray-200 animate-pulse rounded-2xl" />
          <div className="h-24 bg-gray-200 animate-pulse rounded-2xl" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Card className="p-4 bg-red-50 border-red-200">
        <p className="text-sm text-red-600">Erro ao carregar métricas: {error}</p>
      </Card>
    )
  }

  if (!metrics) {
    return null
  }

  const saldoPositivo = metrics.saldoAtual >= 0

  return (
    <div className="space-y-3">
      {/* Card grande - Saldo/Realizado */}
      <Card className="p-6 border shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-muted-foreground">
            Realizado no período
          </span>
          {saldoPositivo ? (
            <TrendingUp className="h-5 w-5 text-green-600" />
          ) : (
            <TrendingDown className="h-5 w-5 text-red-600" />
          )}
        </div>
        <p className={`text-3xl font-bold ${
          saldoPositivo ? 'text-green-700' : 'text-red-700'
        }`}>
          {formatCurrency(metrics.saldoAtual)}
        </p>
        <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
          <Activity className="h-3 w-3" />
          <span>{metrics.totalTransacoes} transações</span>
        </div>
      </Card>

      {/* Card unificado - Receitas e Despesas + Botão Importar */}
      <Card className="p-4 border shadow-sm">
        <div className="grid grid-cols-2 gap-4 mb-4">
          {/* Receitas */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-xs font-medium text-muted-foreground">
                Receitas
              </span>
            </div>
            <p className="text-xl font-bold text-green-700">
              {formatCurrency(metrics.totalReceitas)}
            </p>
          </div>

          {/* Despesas */}
          <div>
            <div className="flex items-center gap-2 mb-2">
              <TrendingDown className="h-4 w-4 text-red-600" />
              <span className="text-xs font-medium text-muted-foreground">
                Despesas
              </span>
            </div>
            <p className="text-xl font-bold text-red-700">
              {formatCurrency(metrics.totalDespesas)}
            </p>
          </div>
        </div>

        {/* Botão Importar */}
        <Button
          onClick={() => router.push('/upload')}
          className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Upload className="h-4 w-4 mr-2" />
          Importar Arquivo
        </Button>
      </Card>

      {/* Gráfico histórico colapsável integrado */}
      <Card className="border shadow-sm overflow-hidden">
        {/* Header do gráfico com botão de expansão */}
        <button
          onClick={() => setIsChartExpanded(!isChartExpanded)}
          className="w-full p-4 flex items-center justify-between hover:bg-accent/5 transition-colors"
        >
          <div className="text-left">
            <h3 className="text-sm font-medium text-foreground">
              Receitas vs Despesas
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Histórico dos últimos 12 meses
            </p>
          </div>
          {isChartExpanded ? (
            <ChevronUp className="h-5 w-5 text-muted-foreground flex-shrink-0" />
          ) : (
            <ChevronDown className="h-5 w-5 text-muted-foreground flex-shrink-0" />
          )}
        </button>

        {/* Conteúdo expansível do gráfico */}
        {isChartExpanded && (
          <div className="px-4 pb-4 border-t bg-background">
            {chartLoading ? (
              <div className="h-64 bg-gray-200 animate-pulse rounded-lg mt-4" />
            ) : chartError ? (
              <div className="py-4 text-center">
                <p className="text-sm text-red-600">{chartError}</p>
              </div>
            ) : chartData && chartData.length > 0 ? (
              <div className="mt-4 max-h-[60vh] overflow-auto">
                <ChartAreaInteractive
                  data={chartData}
                  selectedMonth={selectedMonth}
                  onMonthClick={onChartMonthClick}
                />
              </div>
            ) : (
              <div className="py-8 text-center">
                <p className="text-sm text-muted-foreground">Nenhum dado disponível para exibir</p>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  )
}
