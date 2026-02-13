'use client'

/**
 * Goals Mobile - Tela de Metas
 * 
 * Lista de metas (goals) do usuário com progresso
 * Utiliza budget_planning existente como base de dados
 * 
 * Features:
 * - Lista de metas (grupos) com cards
 * - Filtro por status (ativo, concluído, atrasado)
 * - Criar nova meta (novo grupo)
 * - Ver detalhes da meta
 * - Indicador de progresso visual
 * 
 * Endpoints usados:
 * - GET /api/v1/budget/planning?mes_referencia=YYYY-MM
 * - GET /api/v1/budget/planning/grupos-disponiveis
 */

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { Plus, Filter, Target as TargetIcon, Settings } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { GoalCard, DonutChart } from '@/features/goals/components'
import { useGoals } from '@/features/goals/hooks/use-goals'
import { GoalStatus } from '@/features/goals/types'


type FilterOption = 'todos' | 'ativo' | 'concluido' | 'atrasado'

export default function GoalsMobilePage() {
  const router = useRouter()
  const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
  const { goals, loading, error, refreshGoals } = useGoals(selectedMonth)
  const [filterStatus, setFilterStatus] = React.useState<FilterOption>('todos')
  
  // Filtrar metas baseado no status
  const filteredGoals = React.useMemo(() => {
    if (filterStatus === 'todos') return goals
    return goals.filter(goal => {
      const status = goal.status || 'ativo'
      return status === filterStatus
    })
  }, [goals, filterStatus])
  
  // Contar metas por status
  const statusCounts = React.useMemo(() => {
    return {
      todos: goals.length,
      ativo: goals.filter(g => g.status === 'ativo').length,
      concluido: goals.filter(g => g.status === 'concluido').length,
      atrasado: goals.filter(g => g.status === 'atrasado').length
    }
  }, [goals])
  
  const handleGoalClick = (goalId: number) => {
    router.push(`/mobile/budget/${goalId}`)
  }
  
  const handleCreateGoal = () => {
    router.push('/mobile/budget/new')
  }
  
  const handleManageGoals = () => {
    router.push('/mobile/budget/manage')
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Metas"
        leftAction={null}
        rightActions={[
          {
            icon: <Settings className="w-5 h-5" />,
            label: 'Gerenciar metas',
            onClick: handleManageGoals
          },
          {
            icon: <Plus className="w-5 h-5" />,
            label: 'Nova meta',
            onClick: handleCreateGoal
          }
        ]}
      />
      
      {/* Month Picker */}
      <MonthScrollPicker
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
        className="bg-white border-b border-gray-200"
      />
      
      {/* Donut Chart - Visão Geral */}
      {!loading && goals.length > 0 && (
        <div className="bg-white px-6 py-6 border-b border-gray-200">
          <DonutChart goals={goals} selectedMonth={selectedMonth} />
        </div>
      )}
      
      {/* Filtros */}
      <div className="bg-white border-b border-gray-200 px-5 py-3">
        <div className="flex items-center gap-2 overflow-x-auto">
          <button
            onClick={() => setFilterStatus('todos')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filterStatus === 'todos'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Todas ({statusCounts.todos})
          </button>
          <button
            onClick={() => setFilterStatus('ativo')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filterStatus === 'ativo'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Ativas ({statusCounts.ativo})
          </button>
          <button
            onClick={() => setFilterStatus('concluido')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filterStatus === 'concluido'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Concluídas ({statusCounts.concluido})
          </button>
          <button
            onClick={() => setFilterStatus('atrasado')}
            className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
              filterStatus === 'atrasado'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            Atrasadas ({statusCounts.atrasado})
          </button>
        </div>
      </div>
      
      {/* Lista de Metas */}
      <div className="flex-1 overflow-y-auto p-5">
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-500">Carregando metas...</div>
          </div>
        ) : error ? (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="text-red-600 text-center mb-4">
              <div className="font-semibold mb-2">Erro ao carregar metas</div>
              <div className="text-sm">{error}</div>
            </div>
            <button
              onClick={refreshGoals}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg"
            >
              Tentar novamente
            </button>
          </div>
        ) : filteredGoals.length > 0 ? (
          <div className="space-y-4">
            {filteredGoals.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onClick={() => handleGoalClick(goal.id)}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10">
            <TargetIcon className="w-16 h-16 text-gray-300 mb-4" />
            <div className="text-gray-500 text-center">
              <div className="font-semibold mb-2">
                {filterStatus === 'todos' 
                  ? 'Nenhuma meta criada' 
                  : `Nenhuma meta ${filterStatus === 'ativo' ? 'ativa' : filterStatus === 'concluido' ? 'concluída' : 'atrasada'}`
                }
              </div>
              <div className="text-sm mb-4">
                {filterStatus === 'todos'
                  ? 'Crie sua primeira meta para começar'
                  : 'Ajuste os filtros para ver outras metas'
                }
              </div>
              {filterStatus === 'todos' && (
                <button
                  onClick={handleCreateGoal}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium"
                >
                  Criar primeira meta
                </button>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
