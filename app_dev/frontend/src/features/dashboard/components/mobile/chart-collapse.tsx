'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ChevronDown, ChevronUp } from 'lucide-react'
import ChartAreaInteractive from '../chart-area-interactive'

interface ChartDataItem {
  mes: string
  receitas: number
  despesas: number
}

interface ChartCollapseProps {
  chartData: ChartDataItem[]
  selectedMonth: string
  onMonthClick: (month: string) => void
  loading: boolean
  error: string | null
}

export function ChartCollapse({ 
  chartData, 
  selectedMonth, 
  onMonthClick,
  loading,
  error 
}: ChartCollapseProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  if (loading) {
    return (
      <Card className="rounded-2xl shadow-md">
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Receitas vs Despesas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-gray-200 animate-pulse rounded-lg" />
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className="rounded-2xl shadow-md bg-red-50 border-red-200">
        <CardContent className="pt-6">
          <p className="text-sm text-red-600">{error}</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="rounded-2xl shadow-md">
      {/* Header */}
      <CardHeader className="pb-3">
        <CardTitle className="text-base">Receitas vs Despesas</CardTitle>
        <p className="text-xs text-gray-500 mt-1">
          Histórico dos últimos 12 meses
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Botão de expansão */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg border bg-card hover:bg-accent/5 transition-colors"
        >
          <span className="text-sm font-medium text-muted-foreground">
            {isExpanded ? 'Ocultar gráfico' : 'Ver gráfico histórico'}
          </span>
          {isExpanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </button>

        {/* Gráfico expansível */}
        {isExpanded && (
          <div className="pt-2">
            <ChartAreaInteractive
              data={chartData}
              selectedMonth={selectedMonth}
              onMonthClick={onMonthClick}
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
