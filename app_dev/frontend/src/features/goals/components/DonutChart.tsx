'use client'

import { Goal, calculateGoalProgress } from '../types'

interface DonutChartProps {
  goals: Goal[]
  selectedMonth: Date
}

export function DonutChart({ goals, selectedMonth }: DonutChartProps) {
  const totalBudget = goals.reduce((sum, goal) => sum + goal.valor_planejado, 0)
  const totalSpent = goals.reduce((sum, goal) => {
    const { valor_atual } = calculateGoalProgress(goal)
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

  return (
    <div className="relative w-48 h-48 mx-auto">
      <svg className="transform -rotate-90" width="192" height="192" viewBox="0 0 192 192">
        {/* Background circle */}
        <circle
          cx="96"
          cy="96"
          r={radius}
          fill="none"
          stroke="#f3f4f6"
          strokeWidth="14"
        />
        
        {/* Goal segments */}
        {segments.map((segment, index) => (
          <circle
            key={index}
            cx="96"
            cy="96"
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
      
      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <p className="text-[9px] uppercase tracking-wider text-gray-400 font-semibold mb-0.5">
          {monthLabel}
        </p>
        <div className="flex items-baseline">
          <span className="text-3xl font-bold text-gray-800">
            R$ {(totalSpent / 1000).toFixed(1).replace('.', ',')}
          </span>
          <span className="text-xl font-bold text-gray-400 ml-0.5">k</span>
        </div>
        <p className="text-[10px] text-gray-400 mt-0.5">
          de R$ {(totalBudget / 1000).toFixed(1).replace('.', ',')}k
        </p>
        <p className="text-xs font-medium text-gray-500 mt-1">
          {overallPercentage}%
        </p>
      </div>
    </div>
  )
}
