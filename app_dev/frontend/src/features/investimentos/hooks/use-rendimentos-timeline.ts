'use client'

/**
 * Hook para timeline de rendimentos
 */

import { useState, useEffect, useCallback } from 'react'
import { getRendimentosTimeline } from '../services/investimentos-api'
import type { RendimentoMensal, TimelineFilters } from '../types'

export function useRendimentosTimeline(filters: TimelineFilters) {
  const [rendimentos, setRendimentos] = useState<RendimentoMensal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Usar valores primitivos como dependências para evitar re-renders infinitos
  const anoInicio = filters.ano_inicio
  const anoFim = filters.ano_fim

  useEffect(() => {
    let cancelled = false

    async function fetchData() {
      try {
        setLoading(true)
        setError(null)

        const data = await getRendimentosTimeline({ ano_inicio: anoInicio, ano_fim: anoFim })
        
        if (!cancelled) {
          setRendimentos(data)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Erro ao carregar timeline')
          console.error('Erro ao carregar timeline:', err)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, [anoInicio, anoFim])

  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await getRendimentosTimeline({ ano_inicio: anoInicio, ano_fim: anoFim })
      setRendimentos(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao carregar timeline')
    } finally {
      setLoading(false)
    }
  }, [anoInicio, anoFim])

  return {
    rendimentos,
    loading,
    error,
    refresh,
  }
}
