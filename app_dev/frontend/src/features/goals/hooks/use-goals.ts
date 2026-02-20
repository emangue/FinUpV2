/**
 * useGoals Hook
 * Hook customizado para gerenciar metas
 */

import { useState, useEffect } from 'react'
import { Goal, GoalCreate, GoalUpdate } from '../types'
import { fetchGoals, createGoal, updateGoal, deleteGoal } from '../services/goals-api'
import { calculateGoalStatus } from '../lib/utils'

export function useGoals(selectedMonth?: Date) {
  const [goals, setGoals] = useState<Goal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadGoals = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchGoals(selectedMonth)
      
      // Adicionar status calculado e ordenar por valor total (valor_realizado) ou valor planejado
      const goalsWithStatus = data.map(goal => ({
        ...goal,
        status: calculateGoalStatus(goal)
      }))
      const sorted = [...goalsWithStatus].sort((a, b) => {
        const va = a.valor_realizado ?? a.valor_planejado ?? 0
        const vb = b.valor_realizado ?? b.valor_planejado ?? 0
        return vb - va // Maior primeiro
      })
      setGoals(sorted)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar metas')
      console.error('Erro ao carregar metas:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadGoals()
  }, [selectedMonth])

  const addGoal = async (data: GoalCreate, replicarParaAnoTodo = false): Promise<Goal> => {
    const newGoal = await createGoal(data, replicarParaAnoTodo)
    await loadGoals()
    return newGoal
  }

  const editGoal = async (goalId: number, data: GoalUpdate): Promise<Goal> => {
    const updatedGoal = await updateGoal(goalId, data)
    await loadGoals()
    return updatedGoal
  }

  const removeGoal = async (goalId: number): Promise<void> => {
    await deleteGoal(goalId)
    await loadGoals()
  }

  const refreshGoals = () => {
    loadGoals()
  }

  return {
    goals,
    loading,
    error,
    addGoal,
    editGoal,
    removeGoal,
    refreshGoals
  }
}
