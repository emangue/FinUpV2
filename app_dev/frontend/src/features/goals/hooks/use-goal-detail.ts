/**
 * useGoalDetail Hook
 * Hook para detalhes de uma meta específica
 */

import { useState, useEffect } from 'react'
import { Goal } from '../types'
import { fetchGoalById } from '../services/goals-api'
import { calculateGoalStatus } from '../lib/utils'

export function useGoalDetail(goalId: number) {
  const [goal, setGoal] = useState<Goal | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadGoal = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchGoalById(goalId)
      
      // Goal já vem completo do backend, status é calculado via helper se necessário
      setGoal(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar meta')
      console.error('Erro ao carregar meta:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (goalId) {
      loadGoal()
    }
  }, [goalId])

  const refreshGoal = () => {
    loadGoal()
  }

  return {
    goal,
    loading,
    error,
    refreshGoal
  }
}
