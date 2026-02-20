'use client'

/**
 * IncomeGroupsBox - Detalhamento de receitas por fonte
 * Caixa abaixo do donut de receitas (layout similar ao ExpenseGroupsBox)
 */

import type { IncomeSource } from '../types'

const GRAY_COLORS = ['#111827', '#4B5563', '#6B7280', '#9CA3AF', '#D1D5DB']

interface IncomeGroupsBoxProps {
  sources: IncomeSource[]
}

export function IncomeGroupsBox({ sources }: IncomeGroupsBoxProps) {
  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0 }).format(v)

  const total = sources.reduce((s, x) => s + x.total, 0)

  if (sources.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Fontes de Receita</h3>
        <p className="text-xs text-gray-400 text-center py-4">Sem receitas no período</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 mb-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">Fontes de Receita</h3>
      <div className="space-y-4">
        {sources.map((item, i) => {
          const color = GRAY_COLORS[i % GRAY_COLORS.length]
          const pct = total > 0 ? (item.total / total) * 100 : 0

          return (
            <div key={item.fonte} className="pb-4 border-b border-gray-100 last:border-0 last:pb-0">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="w-4 h-4 rounded-full shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-sm font-medium text-gray-900 truncate">{item.fonte}</span>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold text-gray-900">{formatCurrency(item.total)}</p>
                  <p className="text-xs text-gray-500">{item.percentual.toFixed(1)}% do total</p>
                </div>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${pct}%`,
                    backgroundColor: color
                  }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
