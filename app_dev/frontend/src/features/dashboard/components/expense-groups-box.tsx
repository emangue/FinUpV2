'use client'

/**
 * ExpenseGroupsBox - Layout estilo Trackers
 * Caixa abaixo do donut de despesas com barras de progresso vs meta
 * 
 * Layout por linha:
 * - Esquerda: círculo colorido + nome do grupo
 * - Direita: valor gasto + "de R$ X" (meta)
 * - Abaixo: barra horizontal que preenche conforme % gasto/meta
 */

import type { ExpenseSource } from '../types'
import { getGoalColor } from '@/features/goals/lib/colors'

interface ExpenseGroupsBoxProps {
  sources: ExpenseSource[]
}

export function ExpenseGroupsBox({ sources }: ExpenseGroupsBoxProps) {
  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0 }).format(v)

  if (sources.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-4">Categorias de Despesa</h3>
        <p className="text-xs text-gray-400 text-center py-4">Sem despesas no período</p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 mb-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">Categorias de Despesa</h3>
      <div className="space-y-4">
        {sources.map((item, i) => {
          const color = item.color || getGoalColor(item.grupo, i)
          const meta = item.valor_planejado ?? 0
          const pctCompletude = meta > 0 ? (item.total / meta) * 100 : (item.total > 0 ? 100 : 0)
          const barWidth = Math.min(pctCompletude, 100)

          return (
            <div key={item.grupo} className="pb-4 border-b border-gray-100 last:border-0 last:pb-0">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="w-4 h-4 rounded-full shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-sm font-medium text-gray-900 truncate">{item.grupo}</span>
                </div>
                <div className="text-right shrink-0">
                  <p className="text-sm font-semibold text-gray-900">{formatCurrency(item.total)}</p>
                  <p className="text-xs text-gray-500">
                    {meta > 0 ? `de ${formatCurrency(meta)}` : 'sem meta'}
                  </p>
                </div>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${barWidth}%`,
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
