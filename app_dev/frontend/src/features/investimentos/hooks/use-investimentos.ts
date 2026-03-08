'use client'

/**
 * Hook para gerenciar investimentos
 * B2: refatorado para usar endpoint agregado /investimentos/overview
 * Substitui 3 requests paralelos (lista + resumo + distribuição) por 1 único request.
 */

import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  fetchInvestimentosOverview,
  invalidateInvestimentosOverviewCache,
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

  // B2: 1 request agregado em vez de 3 paralelos
  useEffect(() => {
    let cancelled = false

    const loadData = async () => {
      try {
        setLoading(true)
        setError(null)

        const overview = await fetchInvestimentosOverview({
          tipo_investimento: memoizedFilters?.tipo_investimento,
          ativo: memoizedFilters?.ativo,
          anomes: memoizedFilters?.anomes,
        })

        if (!cancelled) {
          if (overview.lista)       setInvestimentos(overview.lista)
          if (overview.resumo)      setResumo(overview.resumo)
          if (overview.distribuicao) setDistribuicao(overview.distribuicao)
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

  // Refresh: invalida cache e recarrega via overview
  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      invalidateInvestimentosOverviewCache()

      const overview = await fetchInvestimentosOverview({
        tipo_investimento: memoizedFilters?.tipo_investimento,
        ativo: memoizedFilters?.ativo,
        anomes: memoizedFilters?.anomes,
      })

      if (overview.lista)        setInvestimentos(overview.lista)
      if (overview.resumo)       setResumo(overview.resumo)
      if (overview.distribuicao) setDistribuicao(overview.distribuicao)
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
