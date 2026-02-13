'use client'

import * as React from 'react'
import { useParams, useRouter } from 'next/navigation'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { useGoalDetail } from '@/features/goals/hooks/use-goal-detail'
import { useEditGoal } from '@/features/goals/hooks/use-edit-goal'
import { EditGoalModal, type EditGoalData } from '@/features/goals/components'
import { calculateGoalProgress } from '@/features/goals/types'
import { ArrowLeft, Edit2 } from 'lucide-react'

export default function GoalDetailPage() {
  const params = useParams()
  const router = useRouter()
  const goalId = params.goalId as string
  
  const { goal, loading, error, refreshGoal } = useGoalDetail(Number(goalId))
  const { updateGoal, deleteGoal } = useEditGoal()
  const [isEditModalOpen, setIsEditModalOpen] = React.useState(false)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error || !goal) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-50 p-4">
        <p className="text-gray-600 mb-4">Meta não encontrada</p>
        <button
          onClick={() => router.back()}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg"
        >
          Voltar
        </button>
      </div>
    )
  }

  const { percentual, valor_atual } = calculateGoalProgress(goal)
  const remaining = goal.valor_planejado - valor_atual
  const percentage = percentual
  
  // SVG circle progress
  const radius = 70
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (circumference * percentage) / 100

  // Modal handlers
  const handleSave = async (data: EditGoalData) => {
    await updateGoal(goal.id, goal.grupo, goal.mes_referencia, data)
    await refreshGoal()
    setIsEditModalOpen(false)
  }

  const handleDelete = async () => {
    await deleteGoal(goal.grupo, goal.mes_referencia)
    router.push('/mobile/budget')
  }

  const getStrokeColor = () => {
    if (percentage >= 100) return '#EF4444' // red
    if (percentage >= 75) return '#F59E0B' // orange
    return '#10B981' // green
  }

  const strokeColor = getStrokeColor()

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Detalhes da Meta"
        leftAction="back"
        rightActions={[
          {
            icon: <Edit2 className="w-5 h-5" />,
            label: 'Editar',
            onClick: () => setIsEditModalOpen(true)
          }
        ]}
      />

      {/* Date */}
      <div className="bg-white px-6 py-2 border-b border-gray-200">
        <p className="text-xs text-gray-400 text-right">
          {new Date().toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
        </p>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-white">
        <div className="px-6 pb-6">
          {/* Goal Header */}
          <div className="pt-6 pb-6 border-b border-gray-100">
            <div className="flex items-start gap-3 mb-6">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <span className="text-2xl">🎯</span>
              </div>
              <div className="flex-1 min-w-0">
                <h2 className="text-xl font-bold text-gray-900">{goal.grupo}</h2>
                <p className="text-sm text-gray-500 mt-1">Orçamento {goal.mes_referencia}</p>
              </div>
              <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-semibold rounded-full whitespace-nowrap">
                Meta
              </span>
            </div>

            {/* Progress Circle Large */}
            <div className="relative flex justify-center items-center h-48 mb-6">
              <svg className="w-full h-full max-w-[200px]" viewBox="0 0 200 200">
                <circle cx="100" cy="100" r={radius} fill="none" stroke="#E5E7EB" strokeWidth="8" />
                <circle
                  cx="100"
                  cy="100"
                  r={radius}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth="10"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={offset}
                  transform="rotate(-90 100 100)"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-bold text-gray-900">{percentage}%</span>
                <span className="text-xs text-gray-400 mt-1">realizado</span>
              </div>
            </div>

            {/* Values Grid */}
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-xs text-gray-500 mb-1">Gasto</p>
                <p className="text-base font-bold text-gray-900">
                  R$ {valor_atual.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Meta</p>
                <p className="text-base font-bold text-gray-900">
                  R$ {goal.valor_planejado.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Restante</p>
                <p className={`text-base font-bold ${remaining > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  R$ {Math.abs(remaining).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>

          {/* Transactions History */}
          <div className="pt-6">
            <h3 className="text-sm font-bold text-gray-900 mb-4">Histórico de Transações</h3>

            {/* TODO: Integrar com transações reais filtradas por grupo */}
            <div className="text-center py-8">
              <p className="text-gray-400 text-sm">
                Histórico de transações em desenvolvimento
              </p>
              <p className="text-xs text-gray-400 mt-2">
                Conectar com GET /transactions/?grupo={goal.grupo}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => router.back()}
            className="bg-white text-gray-700 border border-gray-300 rounded-xl py-3 px-4 font-semibold hover:bg-gray-50 transition-colors"
          >
            Voltar
          </button>
          <button
            onClick={() => setIsEditModalOpen(true)}
            className="bg-blue-600 text-white rounded-xl py-3 px-4 font-semibold hover:bg-blue-700 transition-colors shadow-sm"
          >
            Editar Meta
          </button>
        </div>
      </div>

      {/* Edit Goal Modal */}
      <EditGoalModal
        goal={goal}
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        onSave={handleSave}
        onDelete={handleDelete}
      />
    </div>
  )
}
