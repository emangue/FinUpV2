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
      
      // Adicionar status calculado
      const goalsWithStatus = data.map(goal => ({
        ...goal,
        status: calculateGoalStatus(goal)
      }))
      
      setGoals(goalsWithStatus)
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

  const addGoal = async (data: GoalCreate): Promise<Goal> => {
    const newGoal = await createGoal(data)
    await loadGoals() // Recarregar para ter progresso atualizado
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
