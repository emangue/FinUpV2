'use client'

/**
 * GoalListItem - Sprint E
 * Lista compacta de metas alinhada à spec de Despesas vs Plano
 * Layout: [cor] [grupo] | [highlight] [realizado] / [planejado]
 * Clique no nome para ir ao detalhe
 */

import * as React from 'react'
import { Goal } from '../types'
import { formatCurrency } from '../lib/utils'
import { getGoalColor } from '../lib/colors'

interface GoalListItemProps {
  goal: Goal
  index: number
  onClick: () => void
}

export function GoalListItem({ goal, index, onClick }: GoalListItemProps) {
  const realizado = Math.abs(goal.valor_realizado ?? 0)
  const planejado = goal.valor_planejado ?? 0
  const diff = realizado - planejado
  const pct = planejado > 0 ? (realizado / planejado) * 100 : 0
  const isOver = realizado > planejado
  const color = getGoalColor(goal.grupo, index)
  const highlightText = diff >= 0 ? `+${formatCurrency(diff)}` : `-${formatCurrency(-diff)}`
  const highlightClass =
    diff > 0
      ? 'text-red-500 font-semibold'
      : diff < 0
        ? 'text-emerald-600 font-semibold'
        : 'text-gray-500 font-medium'

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <button
          type="button"
          onClick={onClick}
          className="flex items-center gap-2 shrink-0 min-w-0 text-left group"
        >
          <div
            className="w-2.5 h-2.5 rounded-full shrink-0"
            style={{ backgroundColor: color }}
          />
          <span className="text-sm text-gray-800 truncate group-hover:text-blue-600 group-hover:underline">
            {goal.grupo}
          </span>
        </button>
        <div className="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
          <span className={`text-xs ${highlightClass}`}>{highlightText}</span>
          <span className="text-sm font-semibold text-gray-900">
            {formatCurrency(realizado)}
          </span>
          <span className="text-[9px] text-gray-400">/ {formatCurrency(planejado)}</span>
        </div>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{
            width: `${Math.min(pct, 100)}%`,
            backgroundColor: isOver ? '#f87171' : color,
          }}
        />
      </div>
    </div>
  )
}
