/**
 * Hook React Query para cashflow anual (P3).
 *
 * Substitui o padrão manual (useEffect + getCashflow + cache Map) por
 * deduplicação nativa do React Query:
 *   - Dois componentes chamando useCashflowAnual(2026) simultaneamente
 *     disparam apenas 1 request HTTP (deduplicação automática por queryKey).
 *   - Dados mantidos em cache por staleTime=2min (mesmo TTL do cache manual).
 *   - Invalidação via: queryClient.invalidateQueries({ queryKey: ['plano', 'cashflow', 'anual'] })
 *
 * Migração:
 *   ANTES: useEffect(() => { getCashflow(ano).then(setData) }, [ano])
 *   DEPOIS: const { data, isLoading, error } = useCashflowAnual(ano)
 */

import { useQuery } from '@tanstack/react-query'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import type { CashflowResponse } from '../api'

const BASE = `${API_CONFIG.BACKEND_URL}/api/v1/plano`

async function fetchCashflowAnual(ano: number): Promise<CashflowResponse> {
  const res = await fetchWithAuth(`${BASE}/cashflow?ano=${ano}`)
  if (!res.ok) throw new Error(`Erro ao carregar cashflow anual (${res.status})`)
  return res.json()
}

/**
 * Hook para buscar o cashflow anual com deduplicação React Query.
 *
 * @param ano - Ano a buscar (ex: 2026). Se falsy, a query não é executada.
 * @returns { data, isLoading, error, refetch }
 *
 * @example
 * const { data: cashflow, isLoading } = useCashflowAnual(2026)
 */
export function useCashflowAnual(ano: number | null | undefined) {
  return useQuery<CashflowResponse, Error>({
    queryKey: ['plano', 'cashflow', 'anual', ano],
    queryFn: () => fetchCashflowAnual(ano!),
    staleTime: 2 * 60 * 1000,   // 2 minutos — mesmo TTL do cache manual em api.ts
    enabled: !!ano,              // só executa se ano for válido
  })
}
