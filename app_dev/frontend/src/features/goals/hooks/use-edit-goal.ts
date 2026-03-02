'use client'

/**
 * useEditGoal Hook
 * Gerencia edição e exclusão de metas
 */

import { useState } from 'react'
import { updateGoal, updateGoalValor, deleteGoal as deleteGoalApi } from '../services/goals-api'
import type { EditGoalData } from '../components/EditGoalModal'

export function useEditGoal() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateGoalHandler = async (
    goalId: number,
    _goalNome: string,
    mesReferencia: string,
    data: EditGoalData
  ) => {
    setIsLoading(true)
    setError(null)

    try {
      await updateGoal(goalId, {
        grupo: data.nome,
        mes_referencia: mesReferencia,
        valor_planejado: data.orcamento,
        cor: data.cor
      })

      // Se marcou "aplicar para meses posteriores", propaga valor até dezembro
      // Usa grupo original (_goalNome) para encontrar registros nos outros meses
      if (data.aplicarMesesFuturos) {
        await updateGoalValor(goalId, _goalNome, data.orcamento, mesReferencia, true)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar meta'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const deleteGoal = async (goalId: number) => {
    setIsLoading(true)
    setError(null)

    try {
      await deleteGoalApi(goalId)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao excluir meta'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return {
    updateGoal: updateGoalHandler,
    deleteGoal,
    isLoading,
    error
  }
}
