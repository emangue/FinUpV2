/**
 * Goals Types
 * Tipos TypeScript para o sistema de metas
 * 
 * ⚠️ ATUALIZADO 13/02/2026: Consolidação budget_planning
 * Endpoint: GET /api/v1/budget/planning
 * MUDANÇAS: categoria_geral → grupo, total_mensal removido
 */

export type GoalStatus = 'ativo' | 'concluido' | 'atrasado' | 'inativo'

/** Tipo de plano: gastos ou investimentos (derivado de categoria_geral) */
export type PlanType = 'gastos' | 'investimentos'

export interface Goal {
  // id pode ser null para grupos com gasto mas sem meta definida
  id: number | null
  user_id?: number
  grupo: string                    // ANTES: categoria_geral - nome da meta/grupo
  mes_referencia: string           // Era "prazo" - formato YYYY-MM
  valor_planejado: number          // Era "valor_alvo" ou "orcamento"
  valor_medio_3_meses?: number      // Média calculada dos 3 meses anteriores
  valor_realizado?: number         // Calculado pelo backend a partir de journal_entries
  percentual?: number              // Calculado pelo backend
  ativo?: number                   // 0=inativo, 1=ativo
  categoria_geral?: string         // Despesa, Investimentos, Transferência, Receita (base_grupos_config)
  planType?: PlanType              // 'gastos' | 'investimentos' - derivado de categoria_geral
  cor?: string                     // Cor no donut (hex, ex: #3b82f6)
  subgrupos?: { subgrupo: string; valor: number; percentual: number }[]
  created_at?: string
  updated_at?: string
  status?: GoalStatus              // Adicionado pelo useGoals no frontend
}

export interface GoalCreate {
  grupo: string               // ANTES: categoria_geral - Nome da meta/grupo
  mes_referencia: string      // YYYY-MM
  valor_planejado: number     // Valor objetivo
}

export interface GoalUpdate {
  grupo?: string
  mes_referencia?: string
  valor_planejado?: number
  cor?: string                // Cor no gráfico donut (hex)
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

export interface GoalWithProgress extends Goal {
  status: GoalStatus           // calculado no frontend
  progresso: GoalProgress      // calculado no frontend
}

// ==================== Helper Functions ====================

/**
 * Calcula progresso de uma meta
 * NOTA: Despesas vêm negativas do banco - usa abs() para exibição
 */
export function calculateGoalProgress(goal: Goal, valorRealizado: number = 0): GoalProgress {
  const valor_atual = Math.abs(valorRealizado)  // Sempre positivo para exibição
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
  const percentual = goal.percentual ?? calculateGoalProgress(goal, goal.valor_realizado ?? 0).percentual
  
  if (percentual >= 100) return 'concluido'
  if (percentual >= 90) return 'ativo'
  if (percentual < 50) return 'atrasado'
  return 'ativo'
}
