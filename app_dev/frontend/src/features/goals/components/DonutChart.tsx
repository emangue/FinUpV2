'use client'

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  LabelList,
} from 'recharts'
import { cn } from '@/lib/utils'
import { Goal, calculateGoalProgress } from '../types'
import { getGoalColor } from '../lib/colors'

interface DonutChartProps {
  goals: Goal[]
  selectedMonth: Date
}

/** Top 5 + Outros para o donut; texto central mantido do V5; % nas fatias */
export function DonutChart({ goals, selectedMonth }: DonutChartProps) {
  const totalBudget = goals.reduce((sum, goal) => sum + goal.valor_planejado, 0)
  const totalSpent = goals.reduce((sum, goal) => {
    const { valor_atual } = calculateGoalProgress(goal, goal.valor_realizado ?? 0)
    return sum + valor_atual
  }, 0)
  const overallPercentage = totalBudget > 0 ? Math.round((totalSpent / totalBudget) * 100) : 0

  const sorted = [...goals].sort((a, b) => (b.valor_realizado ?? 0) - (a.valor_realizado ?? 0))
  const top5 = sorted.slice(0, 5)
  const rest = sorted.slice(5)
  const outrosTotal = rest.reduce((s, g) => s + (g.valor_realizado ?? 0), 0)

  const donutItems = top5.map((g, i) => ({
    grupo: g.grupo,
    valor: g.valor_realizado ?? 0,
    color: g.cor || getGoalColor(g.grupo, i)
  }))
  if (outrosTotal > 0) {
    donutItems.push({ grupo: 'Demais', valor: outrosTotal, color: getGoalColor('Demais', 99) })
  }

  const totalParaDonut = donutItems.reduce((s, g) => s + g.valor, 0) || 1
  const pieData = donutItems.map((item) => ({
    name: item.grupo,
    value: item.valor,
    fill: item.color,
    percentual: totalParaDonut > 0 ? (item.valor / totalParaDonut) * 100 : 0
  }))

  const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
  const monthLabel = `${monthNames[selectedMonth.getMonth()]} ${selectedMonth.getFullYear()}`

  const formatCompact = (v: number) => {
    if (v >= 1000) return `R$ ${(v / 1000).toFixed(1).replace('.', ',')}k`
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(v)
  }

  if (donutItems.length === 0) {
    return (
      <div className="space-y-4">
        <div className="relative w-52 h-52 mx-auto flex items-center justify-center">
          <p className="text-sm text-gray-400">Sem dados</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="relative w-56 h-56 mx-auto">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {pieData.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
              <LabelList
                dataKey="percentual"
                position="inside"
                formatter={(val: number) => {
                  if (val < 5) return ''
                  return `${Math.round(val)}%`
                }}
                style={{ fontSize: 12, fontWeight: 500, fill: '#fff' }}
              />
            </Pie>
            <Tooltip
              formatter={(val: number, _name: string, props: unknown) => {
                const pct = (props as { payload?: { percentual?: number } })?.payload?.percentual ?? 0
                return [
                  new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0 }).format(val),
                  `${pct.toFixed(1)}%`
                ]
              }}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
          </PieChart>
        </ResponsiveContainer>
        {/* Texto central (mantido do V5) */}
        <div className="absolute inset-0 flex flex-col items-center justify-center px-2 pointer-events-none">
          <p className="text-[8px] uppercase tracking-wider text-gray-400 font-semibold mb-0.5">{monthLabel}</p>
          <span className="text-xl font-bold text-gray-800 truncate">{formatCompact(totalSpent)}</span>
          <p className="text-[9px] text-gray-400 mt-0.5">de {formatCompact(totalBudget)}</p>
          <p className={cn('text-sm font-bold mt-1', overallPercentage >= 100 ? 'text-red-600' : 'text-gray-600')}>
            {overallPercentage}%
          </p>
        </div>
      </div>
      {/* Legenda - Top 5 + Demais (apenas nome e cor; % fica no gráfico) */}
      <div className="grid grid-cols-2 gap-x-3 gap-y-2 max-w-[280px] mx-auto">
        {donutItems.map((item) => (
          <div key={item.grupo} className="flex items-center gap-2 min-w-0">
            <div className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
            <span className="text-[10px] text-gray-600 overflow-hidden text-ellipsis whitespace-nowrap" title={item.grupo}>
              {item.grupo}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
