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

// ─── CACHE: módulo em memória (N1) ─────────────────────────────────────────────
// Seguro apenas em componentes 'use client' (módulo isolado por usuário no browser).
interface _CacheEntry<T> { value: T; ts: number }
const _cache = new Map<string, _CacheEntry<unknown>>()
// Deduplicação de requests em voo: evita cache stampede quando dois componentes
// chamam a mesma função simultaneamente antes do primeiro request terminar.
const _inflight = new Map<string, Promise<unknown>>()
// Cache por ponto individual — chave: "YYYY-MM-01"
// Permite montar janelas de 7 meses sem nova request quando todos os pontos já foram vistos.
const _pointCache = new Map<string, ChartDataPoint>()

const TTL_2MIN = 2 * 60 * 1000
const TTL_5MIN = 5 * 60 * 1000

function _getCache<T>(key: string, ttl: number): T | undefined {
  const hit = _cache.get(key)
  if (hit && Date.now() - hit.ts < ttl) return hit.value as T
  return undefined
}
function _setCache<T>(key: string, value: T): T {
  _cache.set(key, { value, ts: Date.now() })
  return value
}

/** Deduplica requests concorrentes para a mesma key. Se já houver um request em voo,
 *  retorna a mesma Promise em vez de iniciar um segundo request ao backend. */
function _withInFlight<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  if (_inflight.has(key)) return _inflight.get(key) as Promise<T>
  const p = fetcher().finally(() => _inflight.delete(key))
  _inflight.set(key, p)
  return p
}

/** Computa os 7 meses (chaves YYYY-MM-01) que compõem a janela do gráfico mensal. */
function _chartWindow(year: number, month: number): string[] {
  const keys: string[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(year, month - 1 - i, 1)
    keys.push(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`)
  }
  return keys
}

/** Invalida todo o cache do dashboard (chamar após upload bem-sucedido). */
export function invalidateDashboardCache() {
  _cache.clear()
  _inflight.clear()
  _pointCache.clear()
}

// Back-compat alias
export function invalidateLastMonthCache(source?: LastMonthSource) {
  if (source) {
    _cache.delete(`lastMonth:${source}`)
  } else {
    _cache.clear()
    _inflight.clear()
  }
}
// ────────────────────────────────────────────────────────────────────────────────

/**
 * Busca o último mês com dados para inicializar scrolls.
 * - transactions: journal_entries (transações, metas, dashboard resultado)
 * - patrimonio: investimentos_historico (ativos/passivos, tela investimentos)
 * Cache em memória de 5 minutos (P1-1).
 */
export async function fetchLastMonthWithData(
  source: LastMonthSource = 'transactions'
): Promise<{ year: number; month: number }> {
  const key = `lastMonth:${source}`
  const cached = _getCache<{ year: number; month: number }>(key, TTL_5MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(
      `${BASE_URL}/dashboard/last-month-with-data?source=${source}`
    )
    if (!response.ok) throw new Error(`Failed to fetch last month: ${response.status}`)
    const value: { year: number; month: number } = await response.json()
    return _setCache(key, value)
  })
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
  const key = `metrics:${params}`
  const cached = _getCache<DashboardMetrics>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/metrics?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch metrics: ${response.status}`)
    return _setCache(key, await response.json())
  })
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
  const key = `incomeSources:${params}`
  const cached = _getCache<{ sources: IncomeSource[]; total_receitas: number }>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/income-sources?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch income sources: ${response.status}`)
    return _setCache(key, await response.json())
  })
}

/**
 * Busca dados para gráfico de área (receitas vs despesas) - modo mensal.
 * N4a: Sliding window — se todos os 7 pontos já estão no _pointCache, monta localmente (0 requests).
 */
export async function fetchChartData(
  year: number,
  month?: number
): Promise<ChartDataPoint[]> {
  // N4a. Sliding window: se todos os 7 pontos já estão no _pointCache, monta localmente
  if (month) {
    const keys = _chartWindow(year, month)
    if (keys.every(k => _pointCache.has(k))) {
      return keys.map(k => _pointCache.get(k)!)
    }
  }

  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  const key = `chartData:${params}`
  const cached = _getCache<ChartDataPoint[]>(key, TTL_5MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/chart-data?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch chart data: ${response.status}`)
    const result = await response.json()
    const data: ChartDataPoint[] = result.data || []
    // Popula _pointCache com cada ponto retornado
    for (const point of data) {
      _pointCache.set(point.date, point)
    }
    return _setCache(key, data)
  })
}

/** N4b. Prefetch em background — popula _pointCache sem bloquear a UI. */
export function prefetchChartData(year: number, month: number): void {
  fetchChartData(year, month).catch(() => {})
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
  const key = `chartDataYearly:${params}`
  const cached = _getCache<ChartDataPoint[]>(key, TTL_5MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/chart-data-yearly?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch chart data yearly: ${response.status}`)
    const result = await response.json()
    return _setCache(key, result.data || [])
  })
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
  const key = `expenseSources:${params}`
  const cached = _getCache<{ sources: ExpenseSource[]; total_despesas: number }>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
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

    return _setCache(key, { sources: result, total_despesas: totalDespesas })
  })
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
 * Busca aporte planejado (regular + extraordinário) do cenário principal para o mês.
 * Usa CenarioProjecao da base (inclui aportes extraordinários como 13º, bônus em abril, etc).
 */
export async function fetchAportePrincipalPorMes(
  year: number,
  month: number
): Promise<number> {
  try {
    const params = new URLSearchParams({ year: year.toString(), month: month.toString() })
    const response = await fetchWithAuth(`${BASE_URL}/investimentos/cenarios/principal/aporte-mes?${params}`)
    if (!response.ok) return 0
    const data: { aporte?: number } = await response.json()
    return data.aporte ?? 0
  } catch {
    return 0
  }
}

/**
 * Busca dados do plano para um mês específico (cashflow do plano).
 * Retorna renda_esperada, gastos_recorrentes, gastos_extras_esperados, aporte_planejado.
 */
export interface PlanoCashflowMes {
  renda_esperada: number
  extras_creditos: number   // rendas extras planejadas (13º, bônus, etc.)
  gastos_recorrentes: number
  extras_debitos: number    // despesas extras planejadas (sazonais, parcelas)
  aporte_planejado: number
}

export async function fetchPlanoCashflowMes(
  year: number,
  month: number
): Promise<PlanoCashflowMes | null> {
  const key = `planoCashflow:${year}:${month}`
  const cached = _getCache<PlanoCashflowMes>(key, TTL_5MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    try {
      // P1-3: endpoint dedicado retorna apenas 1 mês (evita 91% de payload desnecessário)
      const response = await fetchWithAuth(
        `${BASE_URL}/plano/cashflow/mes?ano=${year}&mes=${month}&modo_plano=true`
      )
      if (!response.ok) return null
      const mes = await response.json()
      const value: PlanoCashflowMes = {
        renda_esperada: mes.renda_esperada ?? 0,
        extras_creditos: mes.extras_creditos ?? 0,
        gastos_recorrentes: mes.gastos_recorrentes ?? 0,
        extras_debitos: mes.extras_debitos ?? 0,
        aporte_planejado: mes.aporte_planejado ?? 0,
      }
      return _setCache(key, value)
    } catch {
      return null
    }
  })
}

/**
 * Soma aportes planejados do cenário principal para ano ou YTD (Jan..ytdMonth).
 */
export async function fetchAportePrincipalPeriodo(
  year: number,
  ytdMonth?: number
): Promise<number> {
  try {
    const params = new URLSearchParams({ year: year.toString() })
    if (ytdMonth != null) params.append('ytd_month', ytdMonth.toString())
    const response = await fetchWithAuth(`${BASE_URL}/investimentos/cenarios/principal/aporte-periodo?${params}`)
    if (!response.ok) return 0
    const data: { aporte?: number } = await response.json()
    return data.aporte ?? 0
  } catch {
    return 0
  }
}

// ============================================================================
// APORTE INVESTIMENTO DETALHADO — GET /plano/aporte-investimento
// Substitui fetchAportePrincipalPorMes + fetchAportePrincipalPeriodo com uma
// única chamada que retorna composição detalhada (fixo + extras) por mês/ano.
// ============================================================================

export interface AporteExtraDetalhe {
  descricao: string
  valor: number
  recorrencia: string       // unico | anual | semestral | trimestral
  evoluir: boolean
  evolucaoValor: number
  evolucaoTipo: string
}

export interface AporteMesDetalhe {
  mes_referencia: string    // YYYY-MM
  aporte_fixo: number
  aporte_extra: number
  aporte_total: number
  extras: AporteExtraDetalhe[]           // receitas extraordinárias (créditos)
  gastos_extras: number                   // total de débitos extraordinários do mês
  gastos_extras_items: AporteExtraDetalhe[]  // lista de débitos (sazonais, parcelas)
}

export interface AporteInvestimentoResponse {
  fonte: 'cenario' | 'perfil' | null
  cenario_id: number | null
  aporte_fixo_mensal: number
  total_fixo_ano: number
  total_extras_ano: number
  total_gastos_extras_ano: number          // soma dos débitos extraordinários no ano
  total_ano: number
  mes?: AporteMesDetalhe      // preenchido quando ?mes= informado
  meses?: AporteMesDetalhe[]  // preenchido quando sem ?mes
}

/**
 * Nova API unificada de aporte planejado.
 * - Com `month`: retorna `.mes` com detalhes do mês específico (fixo + extras)
 * - Sem `month`: retorna `.meses` com os 12 meses + totais anuais
 * Substitui fetchAportePrincipalPorMes + fetchAportePrincipalPeriodo.
 */
export async function fetchAporteInvestimentoDetalhado(
  year: number,
  month?: number,
): Promise<AporteInvestimentoResponse | null> {
  const params = new URLSearchParams({ ano: year.toString() })
  if (month != null) params.append('mes', month.toString())
  const key = `aporteInvestimento:${params}`
  const cached = _getCache<AporteInvestimentoResponse>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    try {
      const response = await fetchWithAuth(`${BASE_URL}/plano/aporte-investimento?${params}`)
      if (!response.ok) return null
      return _setCache(key, await response.json())
    } catch {
      return null
    }
  })
}

/**
 * Busca Investimentos vs Plano para o tab Orçamento
 */
export async function fetchOrcamentoInvestimentos(
  year: number,
  month?: number,
  ytdMonth?: number
): Promise<OrcamentoInvestimentosResponse> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  if (ytdMonth != null && month == null) params.append('ytd_month', ytdMonth.toString())
  const key = `orcamentoInvestimentos:${params}`
  const cached = _getCache<OrcamentoInvestimentosResponse>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/orcamento-investimentos?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch orcamento investimentos: ${response.status}`)
    return _setCache(key, await response.json())
  })
}

export async function fetchCreditCards(
  year: number,
  month?: number
): Promise<CreditCardExpense[]> {
  const params = new URLSearchParams({ year: year.toString() })
  if (month) params.append('month', month.toString())
  const key = `creditCards:${params}`
  const cached = _getCache<CreditCardExpense[]>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/credit-cards?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch credit cards: ${response.status}`)
    return _setCache(key, await response.json())
  })
}

// ============================================================================
// A2 — Endpoint agregado /dashboard/summary
// 1 request consolida: metrics, chart, income-sources, budget-vs-actual,
// credit-cards, orcamento-investimentos, cashflow-mes, aporte-mes
// ============================================================================

export interface DashboardSummary {
  metrics?: DashboardMetrics
  chart?: { data: ChartDataPoint[] }
  chart_yearly?: { data: ChartDataPoint[] }
  income_sources?: { sources: IncomeSource[]; total_receitas: number }
  budget_vs_actual?: {
    items: { grupo: string; realizado: number; planejado: number }[]
    total_realizado: number
    total_planejado: number
    percentual_geral: number
  }
  credit_cards?: CreditCardExpense[]
  orcamento_investimentos?: OrcamentoInvestimentosResponse
  cashflow_mes?: PlanoCashflowMes | null
  aporte_mes?: { aporte: number } | null
}

/**
 * Busca múltiplas seções do dashboard em 1 único request (A2).
 * Reduz ~60% do tempo de cold start eliminando RTTs paralelos.
 *
 * @param year     - Ano
 * @param month    - Mês (1-12)
 * @param ytdMonth - Mês limite para YTD (quando aplicável)
 * @param sections - Subconjunto de seções (default: todas)
 */
export async function fetchDashboardSummary(
  year: number,
  month: number,
  ytdMonth?: number,
  sections?: string,
): Promise<DashboardSummary> {
  const params = new URLSearchParams({
    year: String(year),
    month: String(month),
  })
  if (ytdMonth != null) params.set('ytd_month', String(ytdMonth))
  if (sections)         params.set('sections', sections)

  const key = `dashboardSummary:${params}`
  const cached = _getCache<DashboardSummary>(key, TTL_2MIN)
  if (cached) return cached

  return _withInFlight(key, async () => {
    const response = await fetchWithAuth(`${BASE_URL}/dashboard/summary?${params}`)
    if (!response.ok) throw new Error(`Failed to fetch dashboard summary: ${response.status}`)
    return _setCache(key, await response.json())
  })
}
