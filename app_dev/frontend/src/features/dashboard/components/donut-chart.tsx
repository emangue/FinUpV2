/**
 * DonutChart Component - Estilo Atelie com Recharts
 * Gráfico de rosca com % nas fatias, sem legenda lateral (caixas abaixo)
 */

'use client'

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  LabelList,
} from 'recharts'
import type { IncomeSource, ExpenseSource } from '../types'
import { getGoalColor } from '@/features/goals/lib/colors'

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

const GRAY_COLORS = ['#111827', '#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB', '#E5E7EB']

export function DonutChart({
  activeTab,
  incomeSources,
  totalReceitas,
  expenseSources,
  totalDespesas
}: DonutChartProps) {
  let items: DonutItem[] = []
  if (activeTab === 'income') {
    items = incomeSources.map((s, i) => ({
      label: s.fonte,
      total: s.total,
      percentual: s.percentual,
      color: GRAY_COLORS[i % GRAY_COLORS.length]
    }))
  } else if (activeTab === 'expenses') {
    const sorted = [...expenseSources].sort((a, b) => b.total - a.total)
    const top5 = sorted.slice(0, 5)
    const rest = sorted.slice(5)
    const outrosTotal = rest.reduce((s, r) => s + r.total, 0)
    const outrosPct = totalDespesas > 0 ? (outrosTotal / totalDespesas) * 100 : 0
    items = top5.map((s, i) => ({
      label: s.grupo,
      total: s.total,
      percentual: s.percentual,
      color: getGoalColor(s.grupo, i)
    }))
    if (rest.length > 0 && outrosTotal > 0) {
      items.push({
        label: 'Outros',
        total: outrosTotal,
        percentual: outrosPct,
        color: getGoalColor('Outros', 99)
      })
    }
  }

  const total = activeTab === 'income' ? totalReceitas : totalDespesas
  const title = activeTab === 'income' ? 'Fontes de Receita' : 'Categorias de Despesa'

  const pieData = items.map((item) => ({
    name: item.label,
    value: item.total,
    fill: item.color,
    percentual: item.percentual
  }))

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

  return (
    <div className="mb-6">
      <h3 className="text-sm font-bold text-gray-900 mb-4">{title}</h3>
      <div className="h-[200px] min-h-[200px] w-full">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={50}
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
                position="outside"
                formatter={(val: number) => `${val.toFixed(0)}%`}
                style={{ fontSize: 10, fill: '#374151' }}
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
              contentStyle={{
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
