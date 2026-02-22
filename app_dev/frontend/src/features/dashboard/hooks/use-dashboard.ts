/**
 * Dashboard Hooks
 * Sprint 3.2 - Dashboard Mobile Redesign
 */

import { useState, useEffect } from 'react'
import {
  fetchDashboardMetrics,
  fetchIncomeSources,
  fetchExpenseSources,
  fetchChartData,
  fetchChartDataYearly
} from '../services/dashboard-api'
import type { DashboardMetrics, IncomeSource, ExpenseSource, ChartDataPoint } from '../types'

/**
 * Hook para buscar métricas do dashboard
 * ytdMonth: quando informado com month undefined, retorna YTD (Jan..ytdMonth)
 */
export function useDashboardMetrics(year: number, month?: number, ytdMonth?: number) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchDashboardMetrics(year, month, ytdMonth)
        if (!cancelled) setMetrics(data)
      } catch (err) {
        if (!cancelled) setError(err as Error)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [year, month, ytdMonth])

  return { metrics, loading, error }
}

/**
 * Hook para buscar fontes de receita
 */
export function useIncomeSources(year: number, month?: number) {
  const [sources, setSources] = useState<IncomeSource[]>([])
  const [totalReceitas, setTotalReceitas] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchIncomeSources(year, month)
        if (!cancelled) {
          setSources(data.sources)
          setTotalReceitas(data.total_receitas)
        }
      } catch (err) {
        if (!cancelled) setError(err as Error)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [year, month])

  return { sources, totalReceitas, loading, error }
}

/**
 * Hook para buscar dados do gráfico
 */
export function useChartData(year: number, month?: number) {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        setError(null)
        const data = await fetchChartData(year, month)
        if (!cancelled) setChartData(data)
      } catch (err) {
        if (!cancelled) setError(err as Error)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [year, month])

  return { chartData, loading, error }
}

/**
 * Hook para buscar dados do gráfico por ano (YTD ou ano inteiro)
 */
export function useChartDataYearly(
  years: number[],
  ytdMonth?: number
) {
  const [chartData, setChartData] = useState<ChartDataPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      if (!years.length) {
        setChartData([])
        setLoading(false)
        return
      }
      try {
        setLoading(true)
        setError(null)
        const data = await fetchChartDataYearly(years, ytdMonth)
        if (!cancelled) setChartData(data)
      } catch (err) {
        if (!cancelled) setError(err as Error)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [years.join(','), ytdMonth])

  return { chartData, loading, error }
}

/**
 * Hook para buscar fontes de despesa (budget_planning)
 * TOP 5 grupos + "Outros"
 */
export function useExpenseSources(year: number, month?: number) {
  const [sources, setSources] = useState<ExpenseSource[]>([])
  const [totalDespesas, setTotalDespesas] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        setLoading(true)
        setError(null)
        console.log('🔍 useExpenseSources - Buscando despesas:', { year, month })
        const data = await fetchExpenseSources(year, month)
        console.log('✅ useExpenseSources - Dados recebidos:', data)
        if (!cancelled) {
          setSources(data.sources)
          setTotalDespesas(data.total_despesas)
          console.log('📊 useExpenseSources - Sources:', data.sources)
          console.log('💰 useExpenseSources - Total:', data.total_despesas)
        }
      } catch (err) {
        if (!cancelled) setError(err as Error)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => { cancelled = true }
  }, [year, month])

  return { sources, totalDespesas, loading, error }
}
