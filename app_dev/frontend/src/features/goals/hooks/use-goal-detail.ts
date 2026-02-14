/**
 * useGoalDetail Hook
 * Hook para detalhes de uma meta específica
 * mesReferencia: opcional, usado como fallback quando GET por ID retorna 404
 */

import { useState, useEffect } from 'react'
import { Goal } from '../types'
import { fetchGoalById } from '../services/goals-api'
import { calculateGoalStatus } from '../lib/utils'

export function useGoalDetail(goalId: number, mesReferencia?: string) {
  const [goal, setGoal] = useState<Goal | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const loadGoal = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await fetchGoalById(goalId, mesReferencia)
      
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
  }, [goalId, mesReferencia])

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
