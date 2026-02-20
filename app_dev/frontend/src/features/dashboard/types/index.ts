/**
 * Dashboard Types
 * Sprint 3.2 - Dashboard Mobile Redesign
 */

export interface MonthlyData {
  month: string
  year: number
  income: number
  expenses: number
}

export interface IncomeSource {
  fonte: string
  total: number
  percentual: number
  num_transacoes: number
  color?: string
}

export interface ExpenseSource {
  grupo: string
  total: number
  percentual: number
  valor_planejado?: number  // Meta do grupo (para comparação vs plano)
  color?: string
}

export interface DashboardMetrics {
  total_despesas: number
  total_receitas: number
  total_cartoes: number
  saldo_periodo: number
  num_transacoes: number
  change_percentage?: number | null
  receitas_change_percentage?: number | null
  despesas_vs_plano_percent?: number | null
  ativos_mes?: number | null
  passivos_mes?: number | null
  patrimonio_liquido_mes?: number | null
  ativos_change_percentage?: number | null
  passivos_change_percentage?: number | null
  patrimonio_change_percentage?: number | null
  patrimonio_vs_plano_percent?: number | null
}

export interface ChartDataPoint {
  date: string
  receitas: number
  despesas: number
}
