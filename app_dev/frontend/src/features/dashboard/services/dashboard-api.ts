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

export type LastMonthSource = 'transactions' | 'patrimonio'

/**
 * Busca o último mês com dados para inicializar scrolls.
 * - transactions: journal_entries (transações, metas, dashboard resultado)
 * - patrimonio: investimentos_historico (ativos/passivos, tela investimentos)
 */
export async function fetchLastMonthWithData(
  source: LastMonthSource = 'transactions'
): Promise<{ year: number; month: number }> {
  const response = await fetchWithAuth(
    `${BASE_URL}/dashboard/last-month-with-data?source=${source}`
  )
  if (!response.ok) throw new Error(`Failed to fetch last month: ${response.status}`)
  return response.json()
}

/**
 * Busca métricas principais do dashboard
 * Nova feature: change_percentage (variação % vs mês anterior)
 * ytdMonth: quando informado com month undefined, retorna YTD (Jan..ytdMonth)
 */
export async function fetchDashboardMetrics(
  year: number,
  month?: number,
  ytdMonth?: number
): Promise<DashboardMetrics> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  if (ytdMonth != null && month == null) params.append('ytd_month', ytdMonth.toString())
  
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
 * Busca dados para gráfico de área (receitas vs despesas) - modo mensal
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
 * Busca dados para gráfico por ano (YTD ou ano inteiro)
 * @param years - Lista de anos (ex: [2023, 2024, 2025])
 * @param ytdMonth - Se informado, soma Jan..ytdMonth de cada ano (YTD). Se undefined, ano inteiro.
 */
export async function fetchChartDataYearly(
  years: number[],
  ytdMonth?: number
): Promise<ChartDataPoint[]> {
  if (!years.length) return []
  const params = new URLSearchParams({ years: years.join(',') })
  if (ytdMonth != null) params.append('ytd_month', ytdMonth.toString())
  
  const response = await fetchWithAuth(`${BASE_URL}/dashboard/chart-data-yearly?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch chart data yearly: ${response.status}`)
  
  const result = await response.json()
  return result.data || []
}

/**
 * Busca breakdown de despesas por grupo.
 * Usa dashboard/budget-vs-actual (mesmo plano da tabela de orçamento).
 * TOP 5 grupos + "Outros"
 */
export async function fetchExpenseSources(
  year: number,
  month?: number
): Promise<{ sources: ExpenseSource[]; total_despesas: number }> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  else params.append('ytd', 'true')

  const response = await fetchWithAuth(`${BASE_URL}/dashboard/budget-vs-actual?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch expense sources: ${response.status}`)

  const data = await response.json()
  const items = data.items || []

  // Filtrar apenas grupos com realizado > 0 e ordenar por valor
  const expenses = items
    .filter((item: any) => (item.realizado ?? 0) > 0)
    .map((item: any) => ({
      grupo: item.grupo,
      total: item.realizado ?? 0,
      percentual: item.percentual ?? 0,
      valor_planejado: item.planejado ?? 0
    }))
    .sort((a: any, b: any) => b.total - a.total)

  const totalDespesas = data.total_realizado ?? expenses.reduce((sum: number, item: any) => sum + item.total, 0)

  // TOP 5 + Outros (plano de Outros = soma do planejado dos grupos 6+)
  const top5 = expenses.slice(0, 5)
  const others = expenses.slice(5)

  let result: ExpenseSource[] = top5.map((item: any) => ({
    ...item,
    valor_planejado: item.valor_planejado ?? 0
  }))

  if (others.length > 0) {
    const outrosTotal = others.reduce((sum: number, item: any) => sum + item.total, 0)
    const outrosPlanejado = others.reduce((sum: number, item: any) => sum + (item.valor_planejado ?? 0), 0)
    const outrosPercentual = totalDespesas > 0 ? (outrosTotal / totalDespesas) * 100 : 0
    result.push({
      grupo: 'Outros',
      total: outrosTotal,
      percentual: outrosPercentual,
      valor_planejado: outrosPlanejado
    })
  }

  return { sources: result, total_despesas: totalDespesas }
}

export interface CreditCardExpense {
  cartao: string
  total: number
  percentual: number
  num_transacoes: number
}

/**
 * Busca gastos por cartão de crédito.
 * Usa GET /dashboard/credit-cards
 */
export interface OrcamentoInvestimentosItem {
  grupo: string
  valor: number
  plano: number
}

export interface OrcamentoInvestimentosResponse {
  total_investido: number
  total_planejado: number
  items: OrcamentoInvestimentosItem[]
}

/**
 * Busca Budget vs Actual (raw) para o tab Orçamento
 */
export async function fetchBudgetVsActual(
  year: number,
  month?: number
): Promise<{
  items: { grupo: string; realizado: number; planejado: number }[]
  total_realizado: number
  total_planejado: number
  percentual_geral: number
}> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  else params.append('ytd', 'true')

  const response = await fetchWithAuth(`${BASE_URL}/dashboard/budget-vs-actual?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch budget vs actual: ${response.status}`)

  const data = await response.json()
  return {
    items: data.items || [],
    total_realizado: data.total_realizado ?? 0,
    total_planejado: data.total_planejado ?? 0,
    percentual_geral: data.percentual_geral ?? 0,
  }
}

/**
 * Busca Investimentos vs Plano para o tab Orçamento
 */
export async function fetchOrcamentoInvestimentos(
  year: number,
  month?: number
): Promise<OrcamentoInvestimentosResponse> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())

  const response = await fetchWithAuth(`${BASE_URL}/dashboard/orcamento-investimentos?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch orcamento investimentos: ${response.status}`)

  return response.json()
}

export async function fetchCreditCards(
  year: number,
  month?: number
): Promise<CreditCardExpense[]> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())

  const response = await fetchWithAuth(`${BASE_URL}/dashboard/credit-cards?${params}`)
  if (!response.ok) throw new Error(`Failed to fetch credit cards: ${response.status}`)

  return response.json()
}
