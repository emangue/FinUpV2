/**
 * Components index - Export de componentes compartilhados da feature investimentos
 */

export { DashboardInvestimentos } from './dashboard-investimentos'
export { PortfolioOverview } from './portfolio-overview'
export { TimelineIndicators } from './timeline-indicators'
export { InvestmentsTable } from './investments-table'
export { DistribuicaoChart } from './distribuicao-chart'
export { DistribuicaoPorTipo } from './distribuicao-por-tipo'
export { EvolucaoTemporal } from './evolucao-temporal'
export { VisaoPorCorretora } from './visao-por-corretora'
export { ExportInvestimentos } from './export-investimentos'
export { PeriodFilter } from './period-filter'
export { InvestmentFilters } from './investment-filters'
export { InvestmentDetailsModal } from './investment-details-modal'
export { EditInvestmentModal } from './edit-investment-modal'
export { AddInvestmentModal } from './add-investment-modal'
export { SimuladorCenarios } from './simulador-cenarios'

// Loading & Error States
export { 
  DashboardSkeleton, 
  PortfolioOverviewSkeleton,
  TimelineIndicatorsSkeleton,
  InvestmentsTableSkeleton,
  ChartSkeleton
} from './loading-states'

export { 
  EmptyState,
  EmptyInvestimentos, 
  EmptyFilterResults,
  EmptyDistribuicao,
  EmptyTimeline
} from './empty-states'

export { 
  InvestimentosErrorBoundary,
  ApiErrorFallback
} from './error-boundary'
