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
import { WalletBalanceCard } from '@/features/dashboard/components/wallet-balance-card'
import { BarChart } from '@/features/dashboard/components/bar-chart'
import { DonutChart } from '@/features/dashboard/components/donut-chart'
import { useDashboardMetrics, useIncomeSources, useExpenseSources, useChartData } from '@/features/dashboard/hooks/use-dashboard'
import { fetchLastMonthWithData } from '@/features/dashboard/services/dashboard-api'
import { useRequireAuth } from '@/core/hooks/use-require-auth'

export default function DashboardMobilePage() {
  const router = useRouter()
  const isAuth = useRequireAuth() // 🔐 Hook de proteção de rota
  const [selectedMonth, setSelectedMonth] = useState<Date>(new Date())
  const [period, setPeriod] = useState<YTDToggleValue>('month')
  const [activeTab, setActiveTab] = useState<'income' | 'expenses' | 'budget'>('income')

  // Extrair year e month do selectedMonth
  const year = selectedMonth.getFullYear()
  const month = period === 'month' ? selectedMonth.getMonth() + 1 : undefined

  // ✅ TODOS OS HOOKS PRIMEIRO (antes de any return)
  const { metrics, loading: loadingMetrics } = useDashboardMetrics(year, month)
  const { sources, totalReceitas, loading: loadingSources } = useIncomeSources(year, month)
  const { sources: expenseSources, totalDespesas, loading: loadingExpenses } = useExpenseSources(year, month)
  
  // BarChart precisa de múltiplos meses
  const year2025 = 2025
  const year2026 = 2026
  const { chartData: chartData2025 } = useChartData(year2025, undefined)
  const { chartData: chartData2026, loading: loadingChart } = useChartData(year2026, undefined)
  const chartData = [...chartData2025, ...chartData2026]

  const isLoading = loadingMetrics || loadingSources || loadingExpenses || loadingChart

  // Buscar último mês com dados - APENAS se autenticado
  useEffect(() => {
    if (!isAuth) return
    
    async function loadLastMonth() {
      try {
        const lastMonth = await fetchLastMonthWithData()
        console.log('✅ Último mês com dados:', lastMonth)
        setSelectedMonth(new Date(lastMonth.year, lastMonth.month - 1, 1))
      } catch (error: any) {
        console.error('❌ Erro ao buscar último mês:', error)
      }
    }
    
    loadLastMonth()
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
  
  // Debug: Log de despesas
  console.log('🎯 Dashboard Page - expenseSources:', expenseSources)
  console.log('🎯 Dashboard Page - totalDespesas:', totalDespesas)
  console.log('🎯 Dashboard Page - loadingExpenses:', loadingExpenses)

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Dashboard"
        leftAction={null}
        rightActions={[
          {
            icon: <Download className="w-5 h-5" />,
            label: 'Download',
            onClick: () => console.log('Download clicked')
          }
        ]}
      />

      {/* Date display */}
      <div className="bg-white px-6 py-2">
        <p className="text-xs text-gray-400 text-right">
          {selectedMonth.toLocaleDateString('pt-BR', { month: 'short', year: 'numeric' })}
        </p>
      </div>

      {/* Month Picker */}
      <MonthScrollPicker
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
        className="bg-white border-b border-gray-100"
      />

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
            {/* Wallet Balance Card */}
            <WalletBalanceCard
              balance={metrics?.saldo_periodo || 0}
              changePercentage={metrics?.change_percentage}
            />

            {/* Tabs */}
            <div className="flex gap-6 border-b border-gray-200 mb-6">
              <button
                onClick={() => setActiveTab('income')}
                className={`pb-2 text-sm font-semibold transition-colors ${
                  activeTab === 'income'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Receitas
              </button>
              <button
                onClick={() => setActiveTab('expenses')}
                className={`pb-2 text-sm font-medium transition-colors ${
                  activeTab === 'expenses'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Despesas
              </button>
              <button
                onClick={() => setActiveTab('budget')}
                className={`pb-2 text-sm font-medium transition-colors ${
                  activeTab === 'budget'
                    ? 'text-gray-900 border-b-2 border-gray-900'
                    : 'text-gray-400 hover:text-gray-600'
                }`}
              >
                Orçamento
              </button>
            </div>

            {/* Income Trend Chart */}
            <BarChart
              data={chartData}
              title="Tendência de Receitas"
              totalValue={metrics?.total_receitas || 0}
              selectedMonth={selectedMonth}
            />

            {/* Donut Charts (Income/Expenses) */}
            {(activeTab === 'income' || activeTab === 'expenses') && (
              <DonutChart
                activeTab={activeTab}
                incomeSources={sources}
                totalReceitas={totalReceitas}
                expenseSources={expenseSources}
                totalDespesas={totalDespesas}
              />
            )}

            {/* Recent Transactions */}
            <div className="border-t border-gray-100 pt-4 mt-6">
              <h3 className="text-sm font-bold text-gray-900 mb-3">Transações Recentes</h3>
              <p className="text-xs text-gray-400 text-center py-4">
                Clique em "Ver Todas" para navegar
              </p>
              <button
                onClick={() => router.push('/mobile/transactions')}
                className="w-full py-3 bg-gray-900 text-white rounded-xl font-semibold hover:bg-gray-800 transition-colors"
              >
                Ver Todas as Transações
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
