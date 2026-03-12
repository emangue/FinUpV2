'use client'

/**
 * QueryProvider — wraps the app with React Query's QueryClientProvider.
 *
 * P3: deduplicação de requests de cashflow anual.
 * Quando dois componentes chamam useCashflowAnual(ano) ao mesmo tempo,
 * o React Query dispara apenas 1 request HTTP (deduplicação automática).
 *
 * Configuração global:
 *   staleTime: 2min  → dados são considerados "frescos" por 2 minutos
 *   gcTime: 5min     → cache mantido em memória por 5 minutos após unmount
 *   retry: 1          → 1 retry em caso de erro de rede
 *   refetchOnWindowFocus: false → não refetch ao focar a janela
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 2 * 60 * 1000,       // 2 minutos — cache considerado fresco
            gcTime: 5 * 60 * 1000,           // 5 minutos — mantém em memória após unmount
            retry: 1,                         // 1 retry em erro de rede
            refetchOnWindowFocus: false,      // não refetch ao focar janela (mobile UX)
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}
