/**
 * DonutChart Component
 * Sprint 3.2 - Dashboard Mobile Redesign
 * 
 * Gráfico de rosca para fontes de receita e despesas
 * Fase 2: Suporte para activeTab (income/expenses)
 */

'use client'

import type { IncomeSource, ExpenseSource } from '../types'

type DonutItem = {
  label: string
  total: number
  percentual: number
  color: string
}

interface DonutChartProps {
  activeTab: 'income' | 'expenses' | 'budget'
  incomeSources: IncomeSource[]
  totalReceitas: number
  expenseSources: ExpenseSource[]
  totalDespesas: number
}

// Paleta de cinzas com ALTO CONTRASTE (prototype)
const GRAY_COLORS = [
  '#111827', // gray-900 - quase preto
  '#4B5563', // gray-600 - cinza médio-escuro
  '#6B7280', // gray-500 - cinza médio
  '#9CA3AF', // gray-400 - cinza médio-claro
  '#D1D5DB', // gray-300 - cinza claro
  '#E5E7EB', // gray-200 - cinza muito claro
]

export function DonutChart({ 
  activeTab,
  incomeSources, 
  totalReceitas,
  expenseSources,
  totalDespesas
}: DonutChartProps) {
  // Determinar dados com base na tab ativa
  const items: DonutItem[] = activeTab === 'income'
    ? incomeSources.map((source, index) => ({
        label: source.fonte,
        total: source.total,
        percentual: source.percentual,
        color: GRAY_COLORS[index % GRAY_COLORS.length]
      }))
    : activeTab === 'expenses'
    ? expenseSources.map((source, index) => ({
        label: source.grupo,
        total: source.total,
        percentual: source.percentual,
        color: GRAY_COLORS[index % GRAY_COLORS.length]
      }))
    : []

  const total = activeTab === 'income' ? totalReceitas : totalDespesas
  const title = activeTab === 'income' ? 'Fontes de Receita' : 'Categorias de Despesa'

  if (items.length === 0) {
    return (
      <div className="mb-6">
        <h3 className="text-sm font-bold text-gray-900 mb-4">{title}</h3>
        <p className="text-xs text-gray-400 text-center py-4">
          {activeTab === 'income' ? 'Sem receitas no período' : 'Sem despesas no período'}
        </p>
      </div>
    )
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0
    }).format(value)
  }

  // Calcular strokeDasharray para cada segmento
  const circumference = 2 * Math.PI * 70 // r=70
  let currentOffset = 0

  const segments = items.map((item) => {
    const dashLength = (item.percentual / 100) * circumference
    const segment = {
      ...item,
      dashArray: `${dashLength} ${circumference}`,
      dashOffset: -currentOffset
    }
    currentOffset += dashLength
    return segment
  })

  return (
    <div className="mb-6">
      <h3 className="text-sm font-bold text-gray-900 mb-4">{title}</h3>

      <div className="flex items-center gap-6">
        {/* Donut Chart */}
        <div className="relative w-32 h-32 flex-shrink-0">
          <svg viewBox="0 0 200 200" className="transform -rotate-90 w-full h-full">
            {/* Background circle */}
            <circle
              cx="100"
              cy="100"
              r="70"
              fill="none"
              stroke="#F3F4F6"
              strokeWidth="28"
            />
            {/* Segments */}
            {segments.map((segment, index) => (
              <circle
                key={`segment-${index}`}
                cx="100"
                cy="100"
                r="70"
                fill="none"
                stroke={segment.color}
                strokeWidth="28"
                strokeDasharray={segment.dashArray}
                strokeDashoffset={segment.dashOffset}
                strokeLinecap="round"
              />
            ))}
          </svg>
        </div>

        {/* Legend */}
        <div className="flex-1 space-y-2">
          {items.map((item, index) => (
            <div key={`legend-${index}`} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                ></div>
                <span className="text-xs text-gray-600">{item.label}</span>
              </div>
              <span className={`text-xs font-semibold ${item.total > 0 ? 'text-gray-900' : 'text-gray-400'}`}>
                {item.total > 0 ? formatCurrency(item.total) : '0.00'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
