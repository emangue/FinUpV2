/**
 * useGoals Hook
 * Hook customizado para gerenciar metas
 */

import { useState, useEffect } from 'react'
import { Goal, GoalCreate, GoalUpdate } from '../types'
import { fetchGoals, createGoal, updateGoal, deleteGoal, invalidateGoalsCache } from '../services/goals-api'
import { calculateGoalStatus } from '../lib/utils'

function sortGoals(raw: Goal[]): Goal[] {
  return [...raw].sort((a, b) => {
    const va = a.valor_realizado ?? a.valor_planejado ?? 0
    const vb = b.valor_realizado ?? b.valor_planejado ?? 0
    return vb - va
  })
}

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
      setGoals(sortGoals(goalsWithStatus))
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

  /**
   * Cria meta com optimistic update — UI atualiza imediatamente, sem full refetch.
   * Em caso de erro do servidor, UI volta ao estado anterior (rollback).
   */
  const addGoal = async (data: GoalCreate, replicarParaAnoTodo = false): Promise<Goal> => {
    const optimisticId = -Date.now() as unknown as number  // id temporário negativo, não conflita com reais
    const optimistic: Goal = {
      id: optimisticId,
      grupo: data.grupo,
      mes_referencia: data.mes_referencia,
      valor_planejado: data.valor_planejado,
      valor_realizado: 0,
      percentual: 0,
      ativo: 1,
      status: 'ativo',
    }

    setGoals(prev => sortGoals([...prev, optimistic]))

    try {
      const saved = await createGoal(data, replicarParaAnoTodo)
      invalidateGoalsCache()
      // Substitui o item optimista pelo dado real do servidor
      const savedWithStatus: Goal = { ...saved, status: calculateGoalStatus(saved) }
      setGoals(prev => sortGoals(prev.map(g => g.id === optimisticId ? savedWithStatus : g)))
      return saved
    } catch (err) {
      // Rollback: remove o item optimista
      setGoals(prev => prev.filter(g => g.id !== optimisticId))
      throw err
    }
  }

  /**
   * Edita meta com optimistic update — UI atualiza imediatamente.
   * Rollback para o estado anterior em caso de erro.
   */
  const editGoal = async (goalId: number, data: GoalUpdate): Promise<Goal> => {
    const previousGoals = goals  // snapshot para rollback

    setGoals(prev => sortGoals(prev.map(g =>
      g.id === goalId ? { ...g, ...data, status: calculateGoalStatus({ ...g, ...data }) } : g
    )))

    try {
      const updatedGoal = await updateGoal(goalId, data)
      invalidateGoalsCache()
      // Confirma com dados reais do servidor
      const updatedWithStatus: Goal = { ...updatedGoal, status: calculateGoalStatus(updatedGoal) }
      setGoals(prev => sortGoals(prev.map(g => g.id === goalId ? updatedWithStatus : g)))
      return updatedGoal
    } catch (err) {
      setGoals(sortGoals(previousGoals))  // rollback
      throw err
    }
  }

  /**
   * Remove meta com optimistic update — some da lista imediatamente.
   * Rollback em caso de erro.
   */
  const removeGoal = async (goalId: number): Promise<void> => {
    const previousGoals = goals

    setGoals(prev => prev.filter(g => g.id !== goalId))

    try {
      await deleteGoal(goalId)
      invalidateGoalsCache()
      // Sucesso — UI já está correta
    } catch (err) {
      setGoals(previousGoals)  // rollback
      throw err
    }
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
