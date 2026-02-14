import * as React from 'react'
import { Goal, GoalStatus, calculateGoalProgress, calculateGoalStatus } from '../types'
import { 
  formatCurrency, 
  formatMonth, 
  calculateMonthsRemaining,
  getStatusColor,
  getStatusLabel
} from '../lib/utils'
import { ChevronRight, Target, Calendar, TrendingUp } from 'lucide-react'

interface GoalCardProps {
  goal: Goal
  onClick?: () => void
}

export function GoalCard({ goal, onClick }: GoalCardProps) {
  const status = calculateGoalStatus(goal)
  const progress = calculateGoalProgress(goal, goal.valor_realizado ?? 0)
  const percentual = goal.percentual ?? progress.percentual
  const valor_atual = goal.valor_realizado ?? progress.valor_atual
  const mesesRestantes = calculateMonthsRemaining(goal.mes_referencia)
  
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 active:scale-98 transition-transform cursor-pointer"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <Target className="w-4 h-4 text-blue-600" />
            <h3 className="font-semibold text-gray-900">{goal.grupo}</h3>
          </div>
          <p className="text-sm text-gray-600 line-clamp-1">Orçamento {goal.mes_referencia}</p>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(status)}`}>
            {getStatusLabel(status)}
          </span>
          <ChevronRight className="w-5 h-5 text-gray-400" />
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600">Progresso</span>
          <span className="font-semibold text-gray-900">{percentual}%</span>
        </div>
        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              percentual >= 100 ? 'bg-red-500' :
              percentual >= 75 ? 'bg-amber-500' :
              percentual >= 50 ? 'bg-yellow-500' :
              'bg-green-500'
            }`}
            style={{ width: `${Math.min(percentual, 100)}%` }}
          />
        </div>
      </div>
      
      {/* Valores */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <div className="text-xs text-gray-500 mb-1">Atual</div>
          <div className="font-semibold text-gray-900">
            {formatCurrency(valor_atual)}
          </div>
        </div>
        <div>
          <div className="text-xs text-gray-500 mb-1">Meta</div>
          <div className="font-semibold text-gray-900">
            {formatCurrency(goal.valor_planejado)}
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500 pt-3 border-t border-gray-100">
        <div className="flex items-center gap-1">
          <Calendar className="w-3.5 h-3.5" />
          <span>{formatMonth(goal.mes_referencia)}</span>
        </div>
        {mesesRestantes > 0 && (
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" />
            <span>{mesesRestantes} {mesesRestantes === 1 ? 'mês' : 'meses'} restante{mesesRestantes > 1 ? 's' : ''}</span>
          </div>
        )}
      </div>
    </div>
  )
}
