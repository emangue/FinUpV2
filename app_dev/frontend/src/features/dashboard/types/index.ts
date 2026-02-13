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
  color?: string
}

export interface DashboardMetrics {
  total_despesas: number
  total_receitas: number
  total_cartoes: number
  saldo_periodo: number
  num_transacoes: number
  change_percentage?: number | null
}

export interface ChartDataPoint {
  date: string
  receitas: number
  despesas: number
}
