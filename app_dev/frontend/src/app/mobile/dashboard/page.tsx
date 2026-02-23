'use client'

/**
 * Dashboard Mobile - Redesigned
 * Sprint 3.2 - Substituição completa da tela antiga
 * 
 * Aba Resultado: Mês, YTD e Ano
 * - Mês: scroll de meses, gráfico mensal (últimos 7 meses)
 * - YTD: scroll de anos, gráfico anual (Jan até mês mais recente do ano mais novo)
 * - Ano: scroll de anos, gráfico anual (ano inteiro)
 */

import { useState, useEffect, useMemo } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Download, Upload } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { YearScrollPicker } from '@/components/mobile/year-scroll-picker'
import { YTDToggle, YTDToggleValue } from '@/components/mobile/ytd-toggle'
import { BarChart } from '@/features/dashboard/components/bar-chart'
import { GastosPorCartaoBox } from '@/features/dashboard/components/gastos-por-cartao-box'
import { PatrimonioTab } from '@/features/dashboard/components/patrimonio-tab'
import { OrcamentoTab } from '@/features/dashboard/components/orcamento-tab'
import { PlanoAposentadoriaTab } from '@/features/plano-aposentadoria/components/plano-aposentadoria-tab'
import { useDashboardMetrics, useIncomeSources, useExpenseSources, useChartData, useChartDataYearly } from '@/features/dashboard/hooks/use-dashboard'
import { fetchLastMonthWithData } from '@/features/dashboard/services/dashboard-api'
import { useRequireAuth } from '@/core/hooks/use-require-auth'

const YEARS_RANGE = 7 // Últimos N anos no scroll/gráfico anual

export default function DashboardMobilePage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const isAuth = useRequireAuth() // 🔐 Hook de proteção de rota
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())
  const [selectedYear, setSelectedYear] = useState<number>(new Date().getFullYear())
  const [period, setPeriod] = useState<YTDToggleValue>('month')
  const [activeTab, setActiveTab] = useState<'resultado' | 'patrimonio'>(
    searchParams.get('tab') === 'patrimonio' ? 'patrimonio' : 'resultado'
  )
  const [lastMonthWithData, setLastMonthWithData] = useState<{ year: number; month: number } | null>(null)

  // year/month/ytdMonth para métricas e OrcamentoTab
  const year = period === 'month' ? selectedMonth.getFullYear() : selectedYear
  const month = period === 'month' ? selectedMonth.getMonth() + 1 : undefined
  const ytdMonth = period === 'ytd' ? (lastMonthWithData?.month ?? undefined) : undefined

  // Lista de anos para scroll/gráfico (YTD e Ano)
  const yearsList = useMemo(() => {
    const lastYear = lastMonthWithData?.year ?? new Date().getFullYear()
    const result: number[] = []
    for (let y = lastYear - YEARS_RANGE + 1; y <= lastYear; y++) {
      result.push(y)
    }
    return result
  }, [lastMonthWithData?.year])

  // ✅ TODOS OS HOOKS PRIMEIRO (antes de any return)
  const { metrics, loading: loadingMetrics } = useDashboardMetrics(year, month, ytdMonth)
  const { loading: loadingSources } = useIncomeSources(year, month)
  const { loading: loadingExpenses } = useExpenseSources(year, month)
  
  // Chart data: mensal (Mês) ou anual (YTD/Ano)
  const { chartData: chartDataMonthly, loading: loadingChartMonthly } = useChartData(
    selectedMonth.getFullYear(),
    selectedMonth.getMonth() + 1
  )
  const { chartData: chartDataYearly, loading: loadingChartYearly } = useChartDataYearly(
    yearsList,
    period === 'ytd' ? (lastMonthWithData?.month ?? undefined) : undefined
  )
  
  const chartData = period === 'month' ? chartDataMonthly : chartDataYearly
  const loadingChart = period === 'month' ? loadingChartMonthly : loadingChartYearly

  const isLoading = loadingMetrics || loadingSources || loadingExpenses || loadingChart

  // Default: último mês com dados
  useEffect(() => {
    if (!isAuth) return
    fetchLastMonthWithData('transactions')
      .then((last) => {
        setSelectedMonth(new Date(last.year, last.month - 1, 1))
        setSelectedYear(last.year)
        setLastMonthWithData(last)
      })
      .catch(() => {})
  }, [isAuth])

  // 🔐 Mostrar loading enquanto verifica autenticação (DEPOIS de todos os hooks)
  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Dashboard" leftAction="logo" />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Verificando autenticação...</p>
          </div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Scroll de meses ou anos (conforme período) + ícone Download */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex-1 min-w-0">
            {period === 'month' ? (
              <MonthScrollPicker
                selectedMonth={selectedMonth}
                onMonthChange={setSelectedMonth}
              />
            ) : (
              <YearScrollPicker
                years={yearsList}
                selectedYear={selectedYear}
                onYearChange={setSelectedYear}
              />
            )}
          </div>
          <button
            onClick={() => router.push('/mobile/upload')}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 shrink-0"
            aria-label="Upload"
          >
            <Upload className="w-5 h-5" />
          </button>
          <button
            onClick={() => console.log('Download clicked')}
            className="p-2 rounded-full text-gray-600 hover:bg-gray-100 hover:text-gray-900 shrink-0 mr-1"
            aria-label="Download"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* YTD Toggle */}
      <div className="flex justify-center py-4 bg-white border-b border-gray-200">
        <YTDToggle
          value={period}
          onChange={setPeriod}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto bg-white px-6 pt-6 pb-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-600">Carregando...</div>
          </div>
        ) : (
          <>
            {/* Tabs - Sprint G: 2 abas (Resultado, Patrimônio). Sem KpiCards em Resultado; caixa Patrimônio dentro da aba Patrimônio */}
            <div className="flex gap-6 border-b border-gray-200 mb-6">
              <button
                onClick={() => setActiveTab('resultado')}
                className={`pb-2 text-sm font-semibold transition-colors ${
                  activeTab === 'resultado'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Resultado
              </button>
              <button
                onClick={() => setActiveTab('patrimonio')}
                className={`pb-2 text-sm font-medium transition-colors ${
                  activeTab === 'patrimonio'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Patrimônio
              </button>
            </div>

            {/* Tab Resultado: Resumo + Gráfico (sem Tendência) + Toggle Despesas|Receitas|Cartões + Investimentos + Transações */}
            {activeTab === 'resultado' && (
              <>
                <OrcamentoTab
                  year={year}
                  month={month}
                  variant="resultado"
                  metrics={metrics ? { total_receitas: metrics.total_receitas, total_despesas: metrics.total_despesas } : null}
                  ytdMonth={period === 'ytd' ? lastMonthWithData?.month : undefined}
                  insertBetweenResumoAndRest={
                    <BarChart
                      data={chartData}
                      selectedMonth={selectedMonth}
                      selectedYear={selectedYear}
                      mode={period === 'month' ? 'monthly' : 'yearly'}
                    />
                  }
                  gastosPorCartao={
                    <GastosPorCartaoBox
                      year={year}
                      month={month}
                      monthLabel={
                        month
                          ? `${['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][month - 1]}/${year}`
                          : period === 'ytd'
                            ? `YTD ${year}`
                            : `${year}`
                      }
                    />
                  }
                />
              </>
            )}

            {/* Tab Patrimônio: Caixa Patrimônio dentro da aba + sub-abas Resultado | Plano */}
            {activeTab === 'patrimonio' && (
              <PatrimonioTab
                selectedMonth={selectedMonth}
                variant="dashboard"
                metrics={metrics ?? null}
                planoAposentadoria={
                  <PlanoAposentadoriaTab
                    patrimonioLiquido={metrics?.patrimonio_liquido_mes ?? undefined}
                  />
                }
              />
            )}

            {/* Transações Recentes - Sprint G: apenas na tab Resultado */}
            {activeTab === 'resultado' && (
              <div className="border-t border-gray-100 pt-4 mt-6">
                <h3 className="text-sm font-bold text-gray-900 mb-3">Transações Recentes</h3>
                <button
                  onClick={() => router.push('/mobile/transactions')}
                  className="w-full py-3 bg-gray-900 text-white rounded-xl font-semibold hover:bg-gray-800 transition-colors"
                >
                  Ver Todas as Transações
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
