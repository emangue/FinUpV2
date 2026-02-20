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
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { isSameMonth } from 'date-fns'
import { Plus, Target as TargetIcon, Settings } from 'lucide-react'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { GoalCard, DonutChart } from '@/features/goals/components'
import { useGoals } from '@/features/goals/hooks/use-goals'
import { fetchLastMonthWithData } from '@/features/dashboard/services/dashboard-api'


type FilterOption = 'gastos' | 'investimentos'

function parseMesFromUrl(mes: string | null): Date | null {
  if (!mes || !/^\d{4}-\d{2}$/.test(mes)) return null
  const [y, m] = mes.split('-').map(Number)
  if (m < 1 || m > 12) return null
  return new Date(y, m - 1, 1)
}

function GoalsMobilePageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const mesFromUrl = searchParams.get('mes')
  const initialMonth = React.useMemo(() => parseMesFromUrl(mesFromUrl) ?? new Date(), [mesFromUrl])
  const [selectedMonth, setSelectedMonth] = React.useState<Date>(initialMonth)

  // Sincronizar URL quando o mês mudar (preserva ao voltar do detalhe)
  const handleMonthChange = React.useCallback((month: Date) => {
    setSelectedMonth(month)
    const y = month.getFullYear()
    const m = String(month.getMonth() + 1).padStart(2, '0')
    router.replace(`/mobile/budget?mes=${y}-${m}`, { scroll: false })
  }, [router])

  // Restaurar mês da URL ao navegar de volta (ex: do detalhe)
  React.useEffect(() => {
    const parsed = parseMesFromUrl(mesFromUrl)
    if (parsed && !isSameMonth(parsed, selectedMonth)) {
      setSelectedMonth(parsed)
    }
  }, [mesFromUrl, selectedMonth])

  // Default: último mês com dados (transações) quando não há mes na URL
  React.useEffect(() => {
    if (mesFromUrl) return
    let cancelled = false
    fetchLastMonthWithData('transactions')
      .then(({ year, month }) => {
        if (!cancelled) {
          const m = String(month).padStart(2, '0')
          setSelectedMonth(new Date(year, month - 1, 1))
          router.replace(`/mobile/budget?mes=${year}-${m}`, { scroll: false })
        }
      })
      .catch(() => {
        if (!cancelled) {
          const now = new Date()
          const y = now.getFullYear()
          const m = String(now.getMonth() + 1).padStart(2, '0')
          router.replace(`/mobile/budget?mes=${y}-${m}`, { scroll: false })
        }
      })
    return () => { cancelled = true }
  }, [mesFromUrl, router])
  const { goals, loading, error, refreshGoals } = useGoals(selectedMonth)
  const [filterPlan, setFilterPlan] = React.useState<FilterOption>('gastos')
  
  // Filtrar metas por plano (gastos vs investimentos)
  const filteredGoals = React.useMemo(() => {
    return goals.filter(goal => (goal.planType ?? 'gastos') === filterPlan)
  }, [goals, filterPlan])
  
  // Contar metas por plano
  const planCounts = React.useMemo(() => {
    return {
      gastos: goals.filter(g => (g.planType ?? 'gastos') === 'gastos').length,
      investimentos: goals.filter(g => g.planType === 'investimentos').length
    }
  }, [goals])
  
  const handleGoalClick = (goal: { id: number | null; grupo: string; mes_referencia: string }) => {
    if (goal.id != null) {
      const qs = goal.mes_referencia ? `?mes=${goal.mes_referencia}` : ''
      router.push(`/mobile/budget/${goal.id}${qs}`)
    } else {
      router.push(`/mobile/budget/new?grupo=${encodeURIComponent(goal.grupo)}&mes=${goal.mes_referencia}`)
    }
  }
  
  const handleCreateGoal = () => {
    router.push('/mobile/budget/new')
  }
  
  const handleManageGoals = () => {
    router.push('/mobile/budget/manage')
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      {/* Scroll de meses fixo no topo + botões compactos na mesma linha */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex-1 min-w-0">
            <MonthScrollPicker
              selectedMonth={selectedMonth}
              onMonthChange={handleMonthChange}
            />
          </div>
          <div className="flex items-center gap-1 pr-3 shrink-0">
            <button
              onClick={handleManageGoals}
              className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              aria-label="Gerenciar metas"
            >
              <Settings className="w-5 h-5" />
            </button>
            <button
              onClick={handleCreateGoal}
              className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              aria-label="Nova meta"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Conteúdo rolável - header e mês ficam fixos acima */}
      <div className="flex-1 min-h-0 overflow-y-auto">
        {/* Donut Chart - Visão Geral */}
        {!loading && goals.length > 0 && (
          <div className="bg-white px-6 py-6 border-b border-gray-200">
            <DonutChart goals={goals} selectedMonth={selectedMonth} />
          </div>
        )}
        
        {/* Filtros: Gastos vs Investimentos */}
        <div className="bg-white border-b border-gray-200 px-5 py-3">
          <div className="flex items-center gap-2 overflow-x-auto">
            <button
              onClick={() => setFilterPlan('gastos')}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                filterPlan === 'gastos'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Gastos ({planCounts.gastos})
            </button>
            <button
              onClick={() => setFilterPlan('investimentos')}
              className={`px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${
                filterPlan === 'investimentos'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}
            >
              Investimentos ({planCounts.investimentos})
            </button>
          </div>
        </div>
        
        {/* Lista de Metas */}
        <div className="p-5">
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
                key={goal.id ?? goal.grupo}
                goal={goal}
                onClick={() => handleGoalClick(goal)}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10">
            <TargetIcon className="w-16 h-16 text-gray-300 mb-4" />
            <div className="text-gray-500 text-center">
              <div className="font-semibold mb-2">
                {filterPlan === 'gastos'
                  ? 'Nenhuma meta de gastos'
                  : 'Nenhuma meta de investimentos'
                }
              </div>
              <div className="text-sm mb-4">
                {filterPlan === 'gastos'
                  ? 'Crie metas de gastos ou altere o filtro para investimentos'
                  : 'Crie metas de investimentos ou altere o filtro para gastos'
                }
              </div>
              {planCounts.gastos + planCounts.investimentos === 0 && (
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
    </div>
  )
}

export default function GoalsMobilePage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen text-gray-500">Carregando...</div>}>
      <GoalsMobilePageContent />
    </Suspense>
  )
}
