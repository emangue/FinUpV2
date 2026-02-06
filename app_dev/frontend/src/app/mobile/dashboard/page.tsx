'use client'

/**
 * Dashboard Mobile - Página principal mobile
 * 
 * Integra:
 * - MonthScrollPicker (scroll de meses)
 * - YTDToggle (toggle mês/ano)
 * - MetricCards (métricas reais do backend)
 * - MobileHeader (header unificado)
 * 
 * Baseado no design "Trackers" do Style Guide
 */

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { startOfMonth, endOfMonth, startOfYear, format } from 'date-fns'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { YTDToggle, YTDToggleValue } from '@/components/mobile/ytd-toggle'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'

interface DashboardMetrics {
  receitas: number
  despesas: number
  saldo: number
  investimentos: number
}

export default function DashboardMobilePage() {
  const router = useRouter()
  const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
  const [period, setPeriod] = React.useState<YTDToggleValue>('month')
  const [metrics, setMetrics] = React.useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = React.useState(true)
  
  // Buscar métricas quando mês ou período mudar
  React.useEffect(() => {
    fetchMetrics()
  }, [selectedMonth, period])
  
  const fetchMetrics = async () => {
    try {
      setLoading(true)
      
      // Calcular datas baseado no período
      let startDate: Date
      let endDate: Date
      
      if (period === 'month') {
        // Mês selecionado
        startDate = startOfMonth(selectedMonth)
        endDate = endOfMonth(selectedMonth)
      } else {
        // Year-to-Date (Janeiro até mês selecionado)
        startDate = startOfYear(selectedMonth)
        endDate = endOfMonth(selectedMonth)
      }
      
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      
      // Buscar receitas e despesas do período
      const startDateStr = format(startDate, 'yyyy-MM-dd')
      const endDateStr = format(endDate, 'yyyy-MM-dd')
      
      const response = await fetchWithAuth(
        `${BASE_URL}/transactions/receitas-despesas?data_inicio=${startDateStr}&data_fim=${endDateStr}`
      )
      
      if (response.status === 401) {
        // Token inválido ou expirado - redirecionar para login
        console.error('Não autenticado. Redirecionando para login...')
        router.push('/login')
        return
      }
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      const receitas = data.receitas || 0
      const despesas = data.despesas || 0
      const investimentos = data.investimentos || 0  // Investimentos do período!
      const saldo = data.saldo || 0
      
      setMetrics({
        receitas,
        despesas,
        saldo,
        investimentos
      })
      
    } catch (error) {
      console.error('Erro ao buscar métricas:', error)
      setMetrics({
        receitas: 0,
        despesas: 0,
        saldo: 0,
        investimentos: 0
      })
    } finally {
      setLoading(false)
    }
  }
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Dashboard"
        showBackButton={false}
      />
      
      {/* Month Picker */}
      <MonthScrollPicker
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
        className="bg-white border-b border-gray-200"
      />
      
      {/* YTD Toggle */}
      <div className="flex justify-center py-4 bg-white border-b border-gray-200">
        <YTDToggle
          value={period}
          onChange={setPeriod}
        />
      </div>
      
      {/* Metrics Cards */}
      <div className="flex-1 overflow-y-auto p-5">
        <h1 className="sr-only">Dashboard Financeiro</h1>
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-600">Carregando...</div>
          </div>
        ) : metrics ? (
          <div className="space-y-4">
            {/* Card Receitas */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Receitas</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(metrics.receitas)}
              </div>
            </div>
            
            {/* Card Despesas */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Despesas</div>
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(metrics.despesas)}
              </div>
            </div>
            
            {/* Card Saldo */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Saldo</div>
              <div className={`text-2xl font-bold ${metrics.saldo >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                {formatCurrency(metrics.saldo)}
              </div>
            </div>
            
            {/* Card Investimentos */}
            <div className="bg-white rounded-2xl p-5 shadow-sm">
              <div className="text-sm text-gray-600 mb-1">Investimentos</div>
              <div className="text-2xl font-bold text-purple-600">
                {formatCurrency(metrics.investimentos)}
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-700">Erro ao carregar dados</div>
          </div>
        )}
      </div>
    </div>
  )
}
