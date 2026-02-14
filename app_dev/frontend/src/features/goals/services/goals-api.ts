/**
 * Goals API Service
 * Comunicação com o backend para metas
 * 
 * NOTA: Usa budget_planning existente como base para Goals
 * Um "goal" é representado por múltiplos registros budget_planning
 * agrupados por um identificador comum (grupo + prazo)
 */

import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { Goal, GoalCreate, GoalUpdate } from '../types'

const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`

/**
 * Lista todas as metas do usuário (budget_geral)
 * CORRETO: Retorna interface Goal exata do backend
 */
export async function fetchGoals(selectedMonth?: Date): Promise<Goal[]> {
  const currentDate = selectedMonth || new Date()
  const year = currentDate.getFullYear()
  const month = String(currentDate.getMonth() + 1).padStart(2, '0')
  const mes_referencia = `${year}-${month}`
  
  try {
    const response = await fetchWithAuth(`${BASE_URL}/budget/planning?mes_referencia=${mes_referencia}`)
    
    if (!response.ok) {
      return []
    }
    
    const data = await response.json()
    
    // Backend retorna { mes_referencia, budgets: [...] }
    const budgets = data?.budgets ?? []
    
    return budgets.map((b: any) => ({
      id: b.id,
      grupo: b.grupo,
      mes_referencia: data.mes_referencia || mes_referencia,
      valor_planejado: b.valor_planejado ?? 0,
      valor_realizado: b.valor_realizado ?? 0,
      percentual: b.percentual ?? 0,
      ativo: b.ativo ?? 1,
      valor_medio_3_meses: b.valor_medio_3_meses ?? 0,
      user_id: 0,
      created_at: '',
      updated_at: ''
    }))
    
  } catch (error) {
    console.error('Erro ao buscar metas:', error)
    return []
  }
}

/**
 * Busca uma meta específica por ID
 * Usa GET /budget/planning/{id} - busca direta por ID
 * Fallback: se 404 e mesReferencia informado, busca na lista do mês
 */
export async function fetchGoalById(goalId: number, mesReferencia?: string): Promise<Goal> {
  const response = await fetchWithAuth(`${BASE_URL}/budget/planning/${goalId}`)
  
  if (response.ok) {
    const b = await response.json()
    return {
      id: b.id,
      grupo: b.grupo,
      mes_referencia: b.mes_referencia,
      valor_planejado: b.valor_planejado ?? 0,
      valor_realizado: b.valor_realizado ?? 0,
      percentual: b.percentual ?? 0,
      ativo: b.ativo ?? 1,
      valor_medio_3_meses: b.valor_medio_3_meses ?? 0,
      subgrupos: b.subgrupos ?? [],
      user_id: 0,
      created_at: '',
      updated_at: ''
    }
  }
  
  if (response.status === 404 && mesReferencia) {
    const [year, month] = mesReferencia.split('-').map(Number)
    const refDate = new Date(year, month - 1, 1)
    const goals = await fetchGoals(refDate)
    const goal = goals.find((g: Goal) => g.id === goalId)
    if (goal) return goal
  }
  
  if (response.status === 404) {
    throw new Error('Meta não encontrada')
  }
  throw new Error(`Erro ao buscar meta: ${response.statusText}`)
}

/**
 * Cria nova meta (cria registro em budget_geral)
 * CORRETO: Usa bulk-upsert (backend não tem POST individual)
 */
export async function createGoal(data: GoalCreate): Promise<Goal> {
  const response = await fetchWithAuth(`${BASE_URL}/budget/planning/bulk-upsert`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      mes_referencia: data.mes_referencia,
      budgets: [{
        grupo: data.grupo,
        valor_planejado: data.valor_planejado
      }]
    })
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao criar meta: ${response.statusText}`)
  }
  
  // bulk-upsert retorna array, pegamos primeiro item
  const goals: Goal[] = await response.json()
  return goals[0]
}

/**
 * Atualiza meta existente
 * CORRETO: Usa bulk-upsert (backend não tem PATCH individual para budget_geral)
 */
export async function updateGoal(goalId: number, data: GoalUpdate): Promise<Goal> {
  const response = await fetchWithAuth(`${BASE_URL}/budget/planning/bulk-upsert`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      mes_referencia: data.mes_referencia,
      budgets: [{
        id: goalId,
        grupo: data.grupo,
        valor_planejado: data.valor_planejado
      }]
    })
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao atualizar meta: ${response.statusText}`)
  }
  
  // bulk-upsert retorna array, pegamos primeiro item
  const goals: Goal[] = await response.json()
  return goals[0]
}

/**
 * Deleta meta (deleta budget_planning)
 */
export async function deleteGoal(goalId: number): Promise<void> {
  const response = await fetchWithAuth(`${BASE_URL}/budget/${goalId}`, {
    method: 'DELETE'
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao deletar meta: ${response.statusText}`)
  }
}

/**
 * Toggle ativo/inativo de uma meta (PRESERVA valor_planejado)
 * @param goalId ID do budget_planning
 * @param ativo true para ativar, false para desativar
 */
export async function toggleGoalAtivo(goalId: number, ativo: boolean): Promise<void> {
  const response = await fetchWithAuth(`${BASE_URL}/budget/planning/toggle/${goalId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ ativo })
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao ${ativo ? 'ativar' : 'desativar'} meta: ${response.statusText}`)
  }
}

/**
 * Atualiza APENAS o valor_planejado de uma meta (edição inline)
 * @param goalId ID do budget_planning
 * @param novoValor Novo valor de orçamento
 * @param prazo Mês de referência (YYYY-MM)
 * @param aplicarAteFinAno Se true, aplica para todos os meses seguintes até dezembro
 */
export async function updateGoalValor(
  goalId: number,
  novoValor: number,
  prazo: string,
  aplicarAteFinAno: boolean = false
): Promise<void> {
  try {
    if (aplicarAteFinAno) {
      // Calcular meses de prazo até dezembro do ano atual
      const [ano, mesInicial] = prazo.split('-').map(Number)
      const mesesParaAtualizar: string[] = []
      
      for (let mes = mesInicial; mes <= 12; mes++) {
        const mesFormatado = mes.toString().padStart(2, '0')
        mesesParaAtualizar.push(`${ano}-${mesFormatado}`)
      }
      
      // Fazer múltiplas chamadas (uma por mês)
      const promises = mesesParaAtualizar.map(mesRef =>
        fetchWithAuth(`${BASE_URL}/budget/planning/bulk-upsert`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            mes_referencia: mesRef,
            budgets: [{
              id: goalId,
              valor_planejado: novoValor
            }]
          })
        })
      )
      
      await Promise.all(promises)
    } else {
      // Atualizar apenas o mês atual
      const response = await fetchWithAuth(`${BASE_URL}/budget/planning/bulk-upsert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mes_referencia: prazo,
          budgets: [{
            id: goalId,
            valor_planejado: novoValor
          }]
        })
      })
      
      if (!response.ok) {
        throw new Error(`Erro ao atualizar valor da meta: ${response.statusText}`)
      }
    }
  } catch (error) {
    throw error
  }
}

/**
 * Busca orçamentos vinculados a uma meta
 * (No modelo atual, cada grupo JÁ É um orçamento)
 */
export async function fetchLinkedBudgets(goalId: number) {
  return {
    budgets: [],
    message: 'Funcionalidade em desenvolvimento'
  }
}

/**
 * Vincula/desvincula orçamento à meta
 * (No modelo atual, não aplicável)
 */
export async function toggleBudgetLink(goalId: number, budgetId: number, vincular: boolean) {
  return {
    success: true,
    message: 'Funcionalidade em desenvolvimento'
  }
}
