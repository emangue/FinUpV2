/**
 * Dashboard API Service
 * Sprint 3.2 - Dashboard Mobile Redesign
 * 
 * Integra com as APIs:
 * - GET /dashboard/metrics
 * - GET /dashboard/income-sources
 * - GET /dashboard/chart-data
 */

import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import type { DashboardMetrics, IncomeSource, ExpenseSource, ChartDataPoint } from '../types'

const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`

/**
 * Busca o último mês com dados para inicializar o dashboard
 */
export async function fetchLastMonthWithData(): Promise<{ year: number; month: number }> {
  const response = await fetchWithAuth(`${BASE_URL}/dashboard/last-month-with-data`)
  if (!response.ok) throw new Error(`Failed to fetch last month: ${response.status}`)
  
  return response.json()
}

/**
 * Busca métricas principais do dashboard
 * Nova feature: change_percentage (variação % vs mês anterior)
 */
export async function fetchDashboardMetrics(
  year: number,
  month?: number
): Promise<DashboardMetrics> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  
  const response = await fetchWithAuth(`${BASE_URL}/dashboard/metrics?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch metrics: ${response.status}`)
  
  return response.json()
}

/**
 * Busca breakdown de receitas por fonte (grupo)
 * Nova API criada na Sprint 3.1
 */
export async function fetchIncomeSources(
  year: number,
  month?: number
): Promise<{ sources: IncomeSource[]; total_receitas: number }> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  
  const response = await fetchWithAuth(`${BASE_URL}/dashboard/income-sources?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch income sources: ${response.status}`)
  
  return response.json()
}

/**
 * Busca dados para gráfico de área (receitas vs despesas)
 */
export async function fetchChartData(
  year: number,
  month?: number
): Promise<ChartDataPoint[]> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  
  const response = await fetchWithAuth(`${BASE_URL}/dashboard/chart-data?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch chart data: ${response.status}`)
  
  const result = await response.json()
  return result.data || []
}

/**
 * Busca breakdown de despesas por grupo (budget_planning)
 * TOP 5 grupos + "Outros"
 */
export async function fetchExpenseSources(
  year: number,
  month?: number
): Promise<{ sources: ExpenseSource[]; total_despesas: number }> {
  // Converter year+month para formato mes_referencia (YYYY-MM)
  const mesReferencia = month 
    ? `${year}-${String(month).padStart(2, '0')}`
    : `${year}-01` // Se não tiver mês, usa janeiro
  
  const params = new URLSearchParams({ 
    mes_referencia: mesReferencia
  })
  
  console.log('🌐 fetchExpenseSources - URL:', `${BASE_URL}/budget/planning?${params}`)
  const response = await fetchWithAuth(`${BASE_URL}/budget/planning?${params}`)
  console.log('📡 fetchExpenseSources - Response status:', response.status)
  if (!response.ok) throw new Error(`Failed to fetch expense sources: ${response.status}`)
  
  const data = await response.json()
  console.log('📦 fetchExpenseSources - Raw data:', data)
  console.log('📦 fetchExpenseSources - Budgets array:', data.budgets)
  
  // A resposta tem formato: { mes_referencia, budgets: [{grupo, valor_planejado, valor_realizado, percentual}] }
  // Filtrar apenas grupos com despesas (valores negativos no banco!)
  console.log('🔍 Antes do filtro - total budgets:', data.budgets.length)
  const expenses = data.budgets
    .filter((item: any) => {
      console.log('🔍 Filtrando item:', item.grupo, 'valor_realizado:', item.valor_realizado)
      // Despesas são NEGATIVAS no banco! Filtrar por != 0
      return item.valor_realizado !== 0 && item.valor_realizado !== null
    })
    .map((item: any) => ({
      grupo: item.grupo,
      total: Math.abs(item.valor_realizado), // Usar valor absoluto
      percentual: item.percentual || 0
    }))
    .sort((a: any, b: any) => b.total - a.total)
  
  const totalDespesas = expenses.reduce((sum: number, item: any) => sum + item.total, 0)
  
  // TOP 5 + Outros
  const top5 = expenses.slice(0, 5)
  const others = expenses.slice(5)
  
  let result: ExpenseSource[] = top5
  
  if (others.length > 0) {
    const outrosTotal = others.reduce((sum: number, item: any) => sum + item.total, 0)
    const outrosPercentual = totalDespesas > 0 ? (outrosTotal / totalDespesas) * 100 : 0
    result.push({
      grupo: 'Outros',
      total: outrosTotal,
      percentual: outrosPercentual
    })
  }
  
  return { sources: result, total_despesas: totalDespesas }
}
