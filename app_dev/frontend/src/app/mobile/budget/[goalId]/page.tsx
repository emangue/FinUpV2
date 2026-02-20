'use client'

import * as React from 'react'
import { Suspense } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { useGoalDetail } from '@/features/goals/hooks/use-goal-detail'
import { useEditGoal } from '@/features/goals/hooks/use-edit-goal'
import { EditGoalModal, type EditGoalData } from '@/features/goals/components'
import { calculateGoalProgress } from '@/features/goals/types'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { ArrowLeft, Edit2 } from 'lucide-react'

interface SubgrupoItem {
  subgrupo: string
  valor: number
  percentual: number
}

function GoalSubgrupos({
  grupo,
  mesReferencia,
  subgruposFromGoal,
  onSubgrupoClick
}: {
  grupo: string
  mesReferencia: string
  subgruposFromGoal?: SubgrupoItem[]
  onSubgrupoClick?: (subgrupo: string) => void
}) {
  // Usar subgrupos da meta apenas se existirem (budget = fonte única)
  const hasSubgruposFromGoal = Array.isArray(subgruposFromGoal) && subgruposFromGoal.length > 0
  const [subgrupos, setSubgrupos] = React.useState<SubgrupoItem[]>(subgruposFromGoal ?? [])
  const [loading, setLoading] = React.useState(!hasSubgruposFromGoal)

  React.useEffect(() => {
    if (hasSubgruposFromGoal) {
      setSubgrupos(subgruposFromGoal!)
      setLoading(false)
      return
    }
    const load = async () => {
      try {
        setLoading(true)
        const [year, month] = mesReferencia.split('-').map(Number)
        const url = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/dashboard/subgrupos-by-tipo?year=${year}&month=${month}&grupo=${encodeURIComponent(grupo)}`
        const res = await fetchWithAuth(url)
        if (res.ok) {
          const data = await res.json()
          setSubgrupos(data.subgrupos || [])
        }
      } catch {
        setSubgrupos([])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [grupo, mesReferencia, hasSubgruposFromGoal, subgruposFromGoal?.length])

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2 }).format(v)

  return (
    <div className="pt-6">
      <h3 className="text-sm font-bold text-gray-900 mb-4">Subgrupos</h3>
      {loading ? (
        <div className="py-4 text-center text-gray-400 text-sm">Carregando...</div>
      ) : subgrupos.length === 0 ? (
        <p className="text-gray-400 text-sm py-4">Nenhum subgrupo com transações neste mês</p>
      ) : (
        <div className="space-y-2">
          {subgrupos.map((s) => (
            <button
              key={s.subgrupo}
              type="button"
              onClick={() => onSubgrupoClick?.(s.subgrupo)}
              className="w-full flex justify-between items-center py-2 px-3 bg-gray-50 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors text-left"
            >
              <span className="text-sm font-medium text-gray-700">{s.subgrupo}</span>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">{s.percentual.toFixed(1)}%</span>
                <span className="text-sm font-semibold text-gray-900">{formatCurrency(s.valor)}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

function GoalDetailContent() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const goalId = params.goalId as string
  const mesRef = searchParams.get('mes')
  
  const { goal, loading, error, refreshGoal } = useGoalDetail(Number(goalId), mesRef ?? undefined)
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

  // Despesas vêm negativas do banco - normalizar para exibição (sempre positivo)
  const valor_realizado_raw = goal.valor_realizado ?? 0
  const valor_atual = Math.abs(valor_realizado_raw)
  const percentual = goal.valor_planejado > 0
    ? (valor_atual / goal.valor_planejado) * 100
    : 0
  const remaining = goal.valor_planejado - valor_atual
  const percentage = percentual
  
  // SVG circle progress (cap visual em 100%, mas exibe % real)
  const radius = 70
  const circumference = 2 * Math.PI * radius
  const percentageForCircle = Math.min(percentage, 100)
  const offset = circumference - (circumference * percentageForCircle) / 100

  // Modal handlers
  const handleSave = async (data: EditGoalData) => {
    if (goal.id == null) return
    await updateGoal(goal.id, goal.grupo, goal.mes_referencia, data)
    await refreshGoal()
    setIsEditModalOpen(false)
  }

  const handleDelete = async () => {
    if (goal.id == null) return
    await deleteGoal(goal.id)
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

      {/* Date - sempre do orçamento da meta */}
      <div className="bg-white px-6 py-2 border-b border-gray-200">
        <p className="text-xs text-gray-400 text-right">
          {goal.mes_referencia
            ? new Date(goal.mes_referencia + '-01').toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })
            : new Date().toLocaleDateString('pt-BR', { month: 'long', year: 'numeric' })}
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
              <div className="absolute inset-0 flex flex-col items-center justify-center px-2">
                <span className={`font-bold truncate max-w-full ${percentage >= 100 ? 'text-lg text-red-600' : 'text-xl text-gray-900'}`}>
                  {percentage.toFixed(percentage >= 100 ? 0 : 1)}%
                </span>
                <span className="text-[9px] text-gray-500 mt-0.5 truncate max-w-full">
                  {valor_atual >= 1000
                    ? `R$ ${(valor_atual / 1000).toFixed(1).replace('.', ',')}k`
                    : valor_atual.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })}
                </span>
                <span className="text-[8px] text-gray-400">
                  de {goal.valor_planejado >= 1000
                    ? `R$ ${(goal.valor_planejado / 1000).toFixed(1).replace('.', ',')}k`
                    : goal.valor_planejado.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 })}
                </span>
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
                <p className="text-xs text-gray-500 mb-1">{remaining >= 0 ? 'Restante' : 'Estouro'}</p>
                <p className={`text-base font-bold ${remaining >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {remaining >= 0 ? 'R$ ' : '- R$ '}
                  {Math.abs(remaining).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
            </div>
          </div>

          {/* Subgrupos - mesma fonte que valor realizado */}
          <GoalSubgrupos
            grupo={goal.grupo}
            mesReferencia={goal.mes_referencia}
            subgruposFromGoal={goal.subgrupos}
            onSubgrupoClick={(subgrupo) => {
              const [year, month] = goal.mes_referencia.split('-')
              const params = new URLSearchParams({
                year,
                month,
                grupo: goal.grupo,
                subgrupo: subgrupo === 'Sem subgrupo' ? '__null__' : subgrupo,
                from: 'metas',
                goalId: String(goal.id)
              })
              router.push(`/mobile/transactions?${params}`)
            }}
          />
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

export default function GoalDetailPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col h-screen bg-gray-50 items-center justify-center">
        <div className="text-gray-500">Carregando...</div>
      </div>
    }>
      <GoalDetailContent />
    </Suspense>
  )
}
