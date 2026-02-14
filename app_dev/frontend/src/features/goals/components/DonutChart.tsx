'use client'

import { cn } from '@/lib/utils'
import { Goal, calculateGoalProgress } from '../types'

interface DonutChartProps {
  goals: Goal[]
  selectedMonth: Date
}

export function DonutChart({ goals, selectedMonth }: DonutChartProps) {
  const totalBudget = goals.reduce((sum, goal) => sum + goal.valor_planejado, 0)
  const totalSpent = goals.reduce((sum, goal) => {
    const { valor_atual } = calculateGoalProgress(goal, goal.valor_realizado ?? 0)
    return sum + valor_atual
  }, 0)
  const overallPercentage = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0

  // SVG donut chart calculations
  const radius = 70
  const circumference = 2 * Math.PI * radius
  
  let currentOffset = 0
  const segments = goals.map((goal) => {
    const percentage = (goal.valor_planejado / totalBudget) * 100
    const segmentLength = (circumference * percentage) / 100
    const offset = currentOffset
    currentOffset += segmentLength
    
    return {
      goal,
      percentage,
      offset,
      length: segmentLength,
      color: getSegmentColor(goal.grupo)
    }
  })

  function getSegmentColor(nome: string): string {
    // Cores baseadas no nome do grupo
    const colorMap: Record<string, string> = {
      'Casa': '#3b82f6',
      'Carro': '#10b981',
      'Alimentação': '#f97316',
      'Assinaturas': '#ec4899',
      'Educação': '#a855f7',
      'Saúde': '#06b6d4',
      'Lazer': '#f59e0b',
      'Doações': '#84cc16',
      'Transporte': '#6366f1',
      'Vestuário': '#8b5cf6',
    }
    return colorMap[nome] || '#6b7280'
  }

  // Formatação do mês
  const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
  const monthLabel = `${monthNames[selectedMonth.getMonth()]} ${selectedMonth.getFullYear()}`

  // Formatação compacta para caber no círculo
  const formatCompact = (v: number) => {
    if (v >= 1000) return `R$ ${(v / 1000).toFixed(1).replace('.', ',')}k`
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(v)
  }

  return (
    <div className="relative w-52 h-52 mx-auto">
      <svg className="transform -rotate-90" width="208" height="208" viewBox="0 0 208 208">
        {/* Background circle */}
        <circle
          cx="104"
          cy="104"
          r={radius}
          fill="none"
          stroke="#f3f4f6"
          strokeWidth="14"
        />
        
        {/* Goal segments */}
        {segments.map((segment, index) => (
          <circle
            key={index}
            cx="104"
            cy="104"
            r={radius}
            fill="none"
            stroke={segment.color}
            strokeWidth="16"
            strokeLinecap="round"
            strokeDasharray={`${segment.length} ${circumference - segment.length}`}
            strokeDashoffset={-segment.offset}
            className="cursor-pointer hover:opacity-80 transition-all duration-500"
          />
        ))}
      </svg>
      
      {/* Center text - tamanhos reduzidos para caber melhor */}
      <div className="absolute inset-0 flex flex-col items-center justify-center px-2">
        <p className="text-[8px] uppercase tracking-wider text-gray-400 font-semibold mb-0.5">
          {monthLabel}
        </p>
        <div className="flex items-baseline justify-center max-w-full">
          <span className="text-xl font-bold text-gray-800 truncate">
            {formatCompact(totalSpent)}
          </span>
        </div>
        <p className="text-[9px] text-gray-400 mt-0.5">
          de {formatCompact(totalBudget)}
        </p>
        <p className={cn(
          'text-sm font-bold mt-1',
          overallPercentage >= 100 ? 'text-red-600' : 'text-gray-600'
        )}>
          {overallPercentage}%
        </p>
      </div>
    </div>
  )
}
