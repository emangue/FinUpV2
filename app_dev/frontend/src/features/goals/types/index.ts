/**
 * Goals Types
 * Tipos TypeScript para o sistema de metas
 * 
 * ⚠️ ATUALIZADO 13/02/2026: Consolidação budget_planning
 * Endpoint: GET /api/v1/budget/planning
 * MUDANÇAS: categoria_geral → grupo, total_mensal removido
 */

export interface Goal {
  // ✅ Campos REAIS retornados pelo backend (budget_planning)
  id: number
  user_id: number
  grupo: string                    // ANTES: categoria_geral - nome da meta/grupo
  mes_referencia: string           // Era "prazo" - formato YYYY-MM
  valor_planejado: number          // Era "valor_alvo" ou "orcamento"
  valor_medio_3_meses: number      // Média calculada dos 3 meses anteriores
  created_at: string
  updated_at: string
}

export interface GoalCreate {
  grupo: string               // ANTES: categoria_geral - Nome da meta/grupo
  mes_referencia: string      // YYYY-MM
  valor_planejado: number     // Valor objetivo
}

export interface GoalUpdate {
  grupo?: string              // ANTES: categoria_geral
  mes_referencia?: string
  valor_planejado?: number
}

export interface LinkedBudget {
  id: number
  grupo: string               // ANTES: categoria_geral
  valor_planejado: number
  mes_referencia: string
  vinculado: boolean
}

export interface GoalProgress {
  valor_atual: number          // total_mensal
  valor_objetivo: number       // valor_planejado
  percentual: number           // calculado: (valor_atual / valor_objetivo) * 100
  falta: number                // calculado: valor_objetivo - valor_atual
}

export type GoalStatus = 'ativo' | 'concluido' | 'atrasado' | 'inativo'

export interface GoalWithProgress extends Goal {
  status: GoalStatus           // calculado no frontend
  progresso: GoalProgress      // calculado no frontend
}

// ==================== Helper Functions ====================

/**
 * Calcula progresso de uma meta
 * NOTA: valor_atual vem de transações (não mais do campo total_mensal)
 */
export function calculateGoalProgress(goal: Goal, valorRealizado: number = 0): GoalProgress {
  const valor_atual = valorRealizado  // Passa como parâmetro (buscar de transações)
  const valor_objetivo = goal.valor_planejado
  const percentual = valor_objetivo > 0 ? (valor_atual / valor_objetivo) * 100 : 0
  const falta = Math.max(0, valor_objetivo - valor_atual)
  
  return {
    valor_atual,
    valor_objetivo,
    percentual,
    falta
  }
}

/**
 * Calcula status de uma meta
 */
export function calculateGoalStatus(goal: Goal): GoalStatus {
  const { percentual } = calculateGoalProgress(goal)
  
  if (percentual >= 100) return 'concluido'
  if (percentual >= 90) return 'ativo'
  if (percentual < 50) return 'atrasado'
  return 'ativo'
}
