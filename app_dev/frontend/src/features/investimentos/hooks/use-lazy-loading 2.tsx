/**
 * Hook para lazy loading de componentes
 * Otimiza performance carregando componentes apenas quando necessário
 */

import { lazy, ComponentType } from 'react'
import { Suspense, ReactNode } from 'react'
import { Skeleton } from '@/components/ui/skeleton'

// Skeleton para gráficos de pizza
const ChartSkeleton = () => (
  <div className="space-y-4">
    <Skeleton className="h-6 w-48" />
    <Skeleton className="h-64 w-full rounded-lg" />
    <div className="space-y-2">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-4 w-28" />
      <Skeleton className="h-4 w-36" />
    </div>
  </div>
)

// Skeleton para tabelas
const TableSkeleton = () => (
  <div className="space-y-4">
    <div className="flex items-center space-x-4">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-8 w-32" />
    </div>
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex space-x-4">
          <Skeleton className="h-10 w-32" />
          <Skeleton className="h-10 w-48" />
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-32" />
        </div>
      ))}
    </div>
  </div>
)

// Skeleton para cards de overview
const OverviewSkeleton = () => (
  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    {Array.from({ length: 4 }).map((_, i) => (
      <div key={i} className="border rounded-lg p-6 space-y-4">
        <div className="flex items-center justify-between">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-4 rounded" />
        </div>
        <Skeleton className="h-8 w-20" />
        <Skeleton className="h-3 w-32" />
      </div>
    ))}
  </div>
)

// Função utilitária para criar componentes lazy com Suspense
export function withLazyLoading<T extends {}>(
  lazyComponent: () => Promise<{ default: ComponentType<T> }>,
  fallback: ReactNode = <div>Carregando...</div>
) {
  const LazyComponent = lazy(lazyComponent)
  
  return function WrappedComponent(props: T) {
    return (
      <Suspense fallback={fallback}>
        <LazyComponent {...props} />
      </Suspense>
    )
  }
}

// Componentes lazy pré-configurados para diferentes tipos
export const LazyPieChart = lazy(
  () => import('../components/distribuicao-chart').then(module => ({ default: module.DistribuicaoChart }))
)

export const LazyEvolutionChart = lazy(
  () => import('../components/evolucao-temporal').then(module => ({ default: module.EvolucaoTemporal }))
)

export const LazyInvestmentTable = lazy(
  () => import('../components/investments-table').then(module => ({ default: module.InvestmentsTable }))
)

export const LazyPortfolioOverview = lazy(
  () => import('../components/portfolio-overview').then(m => ({ default: m.PortfolioOverview }))
)

export const LazyTimelineChart = lazy(
  () => import('../components/timeline-indicators').then(m => ({ default: m.TimelineIndicators }))
)

// Hook personalizado para lazy loading condicional
export function useLazyComponent<T>(
  shouldLoad: boolean,
  lazyComponent: () => Promise<{ default: ComponentType<T> }>
) {
  const Component = shouldLoad ? lazy(lazyComponent) : null
  
  return Component
}