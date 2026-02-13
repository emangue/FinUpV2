'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { ArrowLeft, Plus } from 'lucide-react'
import { ManageGoalsListItem } from '@/features/goals/components'
import { useGoals } from '@/features/goals/hooks/use-goals'
import { useEditGoal } from '@/features/goals/hooks/use-edit-goal'
import { Goal } from '@/features/goals/types'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'

export default function ManageGoalsPage() {
  const router = useRouter()
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())
  const { goals, loading, refreshGoals } = useGoals(selectedMonth)
  const { deleteGoal } = useEditGoal()
  const [activeStates, setActiveStates] = useState<Record<string, boolean>>({})
  const [saving, setSaving] = useState(false)

  // Initialize active states when goals load
  useEffect(() => {
    if (goals.length > 0) {
      const initialStates: Record<string, boolean> = {}
      goals.forEach((goal) => {
        // Todas as metas retornadas pelo backend estão ativas por padrão
        initialStates[goal.id] = true
      })
      setActiveStates(initialStates)
    }
  }, [goals])

  const handleToggle = async (goalId: string, currentState: boolean) => {
    // Update local state immediately for better UX
    setActiveStates((prev) => ({ ...prev, [goalId]: !currentState }))

    // Find the goal
    const goal = goals.find((g) => g.id === Number(goalId))
    if (!goal) return

    try {
      // ✅ CORRETO: Usa endpoint toggle que preserva valor_planejado
      const { toggleGoalAtivo } = await import('@/features/goals/services/goals-api')
      await toggleGoalAtivo(Number(goalId), !currentState)
      
      console.log(`✅ Meta ${goal.grupo} ${!currentState ? 'ativada' : 'desativada'}`)
    } catch (error) {
      console.error('Failed to toggle goal:', error)
      // Revert local state on error
      setActiveStates((prev) => ({ ...prev, [goalId]: currentState }))
      alert(`Erro ao ${!currentState ? 'ativar' : 'desativar'} meta`)
    }
  }

  const handleEdit = (goalId: string) => {
    router.push(`/mobile/budget/${goalId}`)
  }
  
  const handleUpdateValor = async (goalId: string, novoValor: number, aplicarAteFinAno: boolean) => {
    const goal = goals.find((g) => g.id === Number(goalId))
    if (!goal) return

    try {
      const { updateGoalValor } = await import('@/features/goals/services/goals-api')
      await updateGoalValor(Number(goalId), novoValor, goal.mes_referencia, aplicarAteFinAno)
      
      console.log(`✅ Valor da meta ${goal.grupo} atualizado: R$ ${novoValor} ${aplicarAteFinAno ? '(até fim do ano)' : '(apenas este mês)'}`)
      
      // Refresh goals to show updated value
      await refreshGoals()
    } catch (error) {
      console.error('Failed to update goal value:', error)
      throw error
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      // Refresh goals to get latest state
      await refreshGoals()
      alert('Alterações salvas com sucesso!')
      router.back()
    } catch (error) {
      console.error('Failed to save changes:', error)
      alert('Erro ao salvar alterações')
    } finally {
      setSaving(false)
    }
  }

  const handleNewGoal = () => {
    // TODO: Navigate to create goal page
    alert('Criar nova meta ainda não implementado')
  }

  // Separate goals by type
  const gastosGoals = goals.filter((g) => g.grupo?.toLowerCase() !== 'investimento')
  const investimentosGoals = goals.filter((g) => g.grupo?.toLowerCase() === 'investimento')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="flex items-center justify-between px-4 py-3">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-gray-700" />
          </button>
          <h1 className="text-lg font-bold text-gray-900">Gerenciar Metas</h1>
          <button
            onClick={handleSave}
            disabled={saving}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors disabled:opacity-50"
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </div>

      {/* Month Picker */}
      <MonthScrollPicker
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
        className="bg-white border-b border-gray-200"
      />

      <div className="max-w-md mx-auto p-4">
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Carregando metas...</p>
          </div>
        ) : (
          <>
            {/* Instructions */}
            <div className="mb-6">
              <p className="text-xs text-gray-500">
                Ative/desative ou edite cada meta individualmente. Use o botão Salvar para
                confirmar as alterações.
              </p>
            </div>

            {/* Goals List */}
            {goals.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">Nenhuma meta encontrada</p>
                <p className="text-sm text-gray-400 mt-2">
                  Crie sua primeira meta para começar
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Gastos Goals */}
                {gastosGoals.length > 0 && (
                  <>
                    {gastosGoals.map((goal) => (
                      <ManageGoalsListItem
                        key={goal.id}
                        goal={goal}
                        isActive={activeStates[goal.id] ?? true}
                        onToggle={handleToggle}
                        onEdit={handleEdit}
                        onUpdateValor={handleUpdateValor}
                      />
                    ))}
                  </>
                )}

                {/* Divider if we have both types */}
                {gastosGoals.length > 0 && investimentosGoals.length > 0 && (
                  <div className="py-2">
                    <div className="border-t border-gray-200"></div>
                    <p className="text-xs text-gray-400 text-center py-2">Investimentos</p>
                  </div>
                )}

                {/* Investimentos Goals */}
                {investimentosGoals.length > 0 && (
                  <>
                    {investimentosGoals.map((goal) => (
                      <ManageGoalsListItem
                        key={goal.id}
                        goal={goal}
                        isActive={activeStates[goal.id] ?? true}
                        onToggle={handleToggle}
                        onEdit={handleEdit}
                        onUpdateValor={handleUpdateValor}
                      />
                    ))}
                  </>
                )}
              </div>
            )}

            {/* New Goal Button */}
            <div className="mt-8">
              <button
                onClick={handleNewGoal}
                className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl py-4 font-bold shadow-lg hover:shadow-xl hover:scale-105 transition-all flex items-center justify-center gap-2"
              >
                <Plus className="w-5 h-5" />
                Nova Meta
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
