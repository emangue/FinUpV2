'use client'

import React, { useState, useEffect } from 'react'
import { fetchWithAuth } from '@/core/utils/api-client'
import { MobileHeader } from '@/features/dashboard/components/mobile/mobile-header'
import { MonthTabs } from '@/features/dashboard/components/mobile/month-tabs'
import { MetricCards } from '@/features/dashboard/components/mobile/metric-cards'
import { BudgetMobile } from '@/features/dashboard/components/mobile/budget-mobile'

interface Metrics {
  totalDespesas: number
  totalReceitas: number
  saldoAtual: number
  totalTransacoes: number
}

interface ChartDataItem {
  mes: string
  receitas: number
  despesas: number
}

export default function DashboardMobilePage() {
  // Estados para dados
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [chartData, setChartData] = useState<ChartDataItem[]>([])
  
  // Estados de loading
  const [loadingMetrics, setLoadingMetrics] = useState(true)
  const [loadingChart, setLoadingChart] = useState(true)
  
  // Estados de erro
  const [metricsError, setMetricsError] = useState<string | null>(null)
  const [chartError, setChartError] = useState<string | null>(null)
  
  // Estados de filtros
  const currentDate = new Date()
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()))
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'))

  const fetchMetrics = async (year: string, month: string) => {
    try {
      setLoadingMetrics(true)
      setMetricsError(null)
      
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL 
        ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` 
        : 'http://localhost:8000/api/v1'
      
      const params = new URLSearchParams({ year })
      if (month !== 'all') {
        params.append('month', month)
      }
      
      const response = await fetchWithAuth(`${apiUrl}/dashboard/metrics?${params}`)
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar métricas: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      setMetrics({
        totalDespesas: data.total_despesas,
        totalReceitas: data.total_receitas,
        saldoAtual: data.saldo_periodo,
        totalTransacoes: data.num_transacoes
      })
      
    } catch (error) {
      console.error('Error fetching metrics:', error)
      setMetricsError(error instanceof Error ? error.message : 'Erro desconhecido')
    } finally {
      setLoadingMetrics(false)
    }
  }

  const fetchChartData = async (year: string, month: string) => {
    try {
      setLoadingChart(true)
      setChartError(null)
      
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL 
        ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` 
        : 'http://localhost:8000/api/v1'
      
      const targetMonth = month === 'all' ? '12' : month
      const params = new URLSearchParams({ year, month: targetMonth })
      
      const response = await fetchWithAuth(`${apiUrl}/dashboard/chart-data?${params}`)
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar dados do gráfico: ${response.statusText}`)
      }
      
      const data = await response.json()
      
      const formattedData = data.data.map((item: any) => ({
        mes: item.date,
        receitas: item.receitas,
        despesas: item.despesas
      }))
      
      setChartData(formattedData)
      
    } catch (error) {
      console.error('Error fetching chart data:', error)
      setChartError(error instanceof Error ? error.message : 'Erro desconhecido')
    } finally {
      setLoadingChart(false)
    }
  }

  const handleMonthChange = (month: string, year: string) => {
    setSelectedMonth(month)
    setSelectedYear(year)
    fetchMetrics(year, month)
    fetchChartData(year, month)
  }

  const handleChartMonthClick = (month: string) => {
    // Ao clicar em um mês no gráfico, atualiza o mês selecionado
    // O ano já é o correto (selectedYear)
    setSelectedMonth(month)
    fetchMetrics(selectedYear, month)
  }

  useEffect(() => {
    fetchMetrics(selectedYear, selectedMonth)
    fetchChartData(selectedYear, selectedMonth)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header fixo com hamburger */}
      <MobileHeader />

      {/* Conteúdo com padding top para compensar header fixo */}
      <div className="pt-16 pb-6 px-4 space-y-4">
        {/* Navegação de meses */}
        <MonthTabs
          selectedYear={selectedYear}
          selectedMonth={selectedMonth}
          onMonthChange={handleMonthChange}
        />

        {/* Cards de métricas com gráfico integrado */}
        <MetricCards
          metrics={metrics}
          loading={loadingMetrics}
          error={metricsError}
          chartData={chartData}
          chartLoading={loadingChart}
          chartError={chartError}
          selectedMonth={selectedMonth}
          onChartMonthClick={handleChartMonthClick}
        />

        {/* Realizado vs Planejado */}
        <BudgetMobile
          year={selectedYear}
          month={selectedMonth}
        />
      </div>
    </div>
  )
}
