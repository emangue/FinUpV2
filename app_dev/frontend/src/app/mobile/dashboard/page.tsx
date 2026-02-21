'use client'

/**
 * Dashboard Mobile - Redesigned
 * Sprint 3.2 - Substituição completa da tela antiga
 * 
 * Novo design baseado no protótipo "Insights":
 * - WalletBalanceCard com change percentage
 * - BarChart (receitas vs despesas mensal)
 * - DonutChart (fontes de receita)
 * - Integração com APIs novas (income-sources, metrics com change%)
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Download } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { YTDToggle, YTDToggleValue } from '@/components/mobile/ytd-toggle'
import { BarChart } from '@/features/dashboard/components/bar-chart'
import { GastosPorCartaoBox } from '@/features/dashboard/components/gastos-por-cartao-box'
import { PatrimonioTab } from '@/features/dashboard/components/patrimonio-tab'
import { OrcamentoTab } from '@/features/dashboard/components/orcamento-tab'
import { PlanoAposentadoriaTab } from '@/features/plano-aposentadoria/components/plano-aposentadoria-tab'
import { useDashboardMetrics, useIncomeSources, useExpenseSources, useChartData } from '@/features/dashboard/hooks/use-dashboard'
import { fetchLastMonthWithData } from '@/features/dashboard/services/dashboard-api'
import { useRequireAuth } from '@/core/hooks/use-require-auth'

export default function DashboardMobilePage() {
  const router = useRouter()
  const isAuth = useRequireAuth() // 🔐 Hook de proteção de rota
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())
  const [period, setPeriod] = useState<YTDToggleValue>('month')
  const [activeTab, setActiveTab] = useState<'resultado' | 'patrimonio'>('resultado')

  // Extrair year e month do selectedMonth
  const year = selectedMonth.getFullYear()
  const month = period === 'month' ? selectedMonth.getMonth() + 1 : undefined

  // ✅ TODOS OS HOOKS PRIMEIRO (antes de any return)
  const { metrics, loading: loadingMetrics } = useDashboardMetrics(year, month)
  const { loading: loadingSources } = useIncomeSources(year, month)
  const { loading: loadingExpenses } = useExpenseSources(year, month)
  
  // BarChart precisa de múltiplos meses
  const year2025 = 2025
  const year2026 = 2026
  const { chartData: chartData2025 } = useChartData(year2025, undefined)
  const { chartData: chartData2026, loading: loadingChart } = useChartData(year2026, undefined)
  const chartData = [...chartData2025, ...chartData2026]

  const isLoading = loadingMetrics || loadingSources || loadingExpenses || loadingChart

  // Default: último mês com dados (journal_entries para resultado/orçamento)
  useEffect(() => {
    if (!isAuth) return
    fetchLastMonthWithData('transactions')
      .then((lastMonth) => setSelectedMonth(new Date(lastMonth.year, lastMonth.month - 1, 1)))
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
      {/* Scroll de meses fixo no topo + ícone Download compacto na mesma linha */}
      <div className="sticky top-0 z-20 bg-white border-b border-gray-200 shrink-0">
        <div className="flex items-center gap-2">
          <div className="flex-1 min-w-0">
            <MonthScrollPicker
              selectedMonth={selectedMonth}
              onMonthChange={setSelectedMonth}
            />
          </div>
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
      <div className="flex-1 overflow-y-auto bg-white px-6 pb-6">
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
                  insertBetweenResumoAndRest={
                    <BarChart
                      data={chartData}
                      title="Receitas vs Despesas"
                      totalValue={(metrics?.total_receitas || 0) + (metrics?.total_despesas || 0)}
                      selectedMonth={selectedMonth}
                    />
                  }
                  gastosPorCartao={
                    <GastosPorCartaoBox
                      year={year}
                      month={month}
                      monthLabel={
                        month
                          ? `${['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][month - 1]}/${year}`
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
