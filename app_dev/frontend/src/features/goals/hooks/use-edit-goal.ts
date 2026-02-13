'use client'

/**
 * useEditGoal Hook
 * Gerencia edição e exclusão de metas
 * 
 * Integra com API POST /api/v1/budget/planning/bulk-upsert
 * Para deletar: envia valor_planejado = 0
 */

import { useState } from 'react'
import { fetchWithAuth } from '@/core/utils/api-client'
import type { EditGoalData } from '../components/EditGoalModal'

interface BulkUpsertPayload {
  mes_referencia: string
  budgets: Array<{
    grupo: string
    valor_planejado: number
  }>
}

export function useEditGoal() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const updateGoal = async (
    goalId: number,
    goalNome: string,
    mesReferencia: string,
    data: EditGoalData
  ) => {
    setIsLoading(true)
    setError(null)

    try {
      // Preparar payload para bulk-upsert
      const payload: BulkUpsertPayload = {
        mes_referencia: mesReferencia,
        budgets: [
          {
            grupo: data.nome, // Novo nome (pode ser igual ao anterior)
            valor_planejado: data.orcamento
          }
        ]
      }

      // Se aplicar para meses futuros, adicionar múltiplos meses
      if (data.aplicarMesesFuturos) {
        // TODO: Implementar lógica de múltiplos meses
        // Por enquanto só atualiza o mês atual
        console.log('TODO: Implementar aplicação para meses futuros')
      }

      const response = await fetchWithAuth(
        'http://localhost:8000/api/v1/budget/planning/bulk-upsert',
        {
          method: 'POST',
          body: JSON.stringify(payload)
        }
      )

      if (!response.ok) {
        throw new Error(`Erro ao atualizar meta: ${response.statusText}`)
      }

      const responseData = await response.json()

      // Se o nome mudou, deletar o grupo antigo
      if (data.nome !== goalNome) {
        await deleteGoal(goalNome, mesReferencia)
      }

      return responseData
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar meta'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  const deleteGoal = async (goalNome: string, mesReferencia: string) => {
    setIsLoading(true)
    setError(null)

    try {
      // Para deletar: enviar valor_planejado = 0
      const payload: BulkUpsertPayload = {
        mes_referencia: mesReferencia,
        budgets: [
          {
            grupo: goalNome,
            valor_planejado: 0
          }
        ]
      }

      const response = await fetchWithAuth(
        'http://localhost:8000/api/v1/budget/planning/bulk-upsert',
        {
          method: 'POST',
          body: JSON.stringify(payload)
        }
      )

      if (!response.ok) {
        throw new Error(`Erro ao excluir meta: ${response.statusText}`)
      }

      return await response.json()
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao excluir meta'
      setError(errorMessage)
      throw new Error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return {
    updateGoal,
    deleteGoal,
    isLoading,
    error
  }
}
