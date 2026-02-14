'use client'

/**
 * Hook para gerenciar investimentos
 * Otimizado com useCallback para performance
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  getInvestimentos,
  getPortfolioResumo,
  getDistribuicaoPorTipo,
} from '../services/investimentos-api'
import type {
  InvestimentoPortfolio,
  PortfolioResumo,
  DistribuicaoTipo,
  InvestimentosFilters,
} from '../types'

export function useInvestimentos(filters?: InvestimentosFilters) {
  const [investimentos, setInvestimentos] = useState<InvestimentoPortfolio[]>([])
  const [resumo, setResumo] = useState<PortfolioResumo | null>(null)
  const [distribuicao, setDistribuicao] = useState<DistribuicaoTipo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Memoizar filters para evitar re-renders desnecessários
  const memoizedFilters = useMemo(() => filters, [JSON.stringify(filters)])

  // useEffect otimizado
  useEffect(() => {
    let cancelled = false

    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)

        const [investimentosData, resumoData, distribuicaoData] = await Promise.all([
          getInvestimentos(memoizedFilters),
          getPortfolioResumo(),
          getDistribuicaoPorTipo(),
        ])

        if (!cancelled) {
          setInvestimentos(investimentosData)
          setResumo(resumoData)
          setDistribuicao(distribuicaoData)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Erro ao carregar dados')
          console.error('Erro ao carregar investimentos:', err)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    loadData()

    return () => {
      cancelled = true
    }
  }, [memoizedFilters])

  // Função refresh otimizada com useCallback
  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const [investimentosData, resumoData, distribuicaoData] = await Promise.all([
        getInvestimentos(memoizedFilters),
        getPortfolioResumo(),
        getDistribuicaoPorTipo(),
      ])
      
      setInvestimentos(investimentosData)
      setResumo(resumoData)
      setDistribuicao(distribuicaoData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar dados')
    } finally {
      setLoading(false)
    }
  }, [memoizedFilters])

  // Memoizar objeto de retorno para evitar re-renders
  return useMemo(() => ({
    investimentos,
    resumo,
    distribuicao,
    loading,
    error,
    refresh,
  }), [investimentos, resumo, distribuicao, loading, error, refresh])
}
