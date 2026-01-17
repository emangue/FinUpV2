/**
 * Página - Investimentos
 */

import { DashboardInvestimentos } from '@/features/investimentos'
import { InvestimentosErrorBoundary } from '@/features/investimentos/components/error-boundary'

export default function InvestimentosPage() {
  return (
    <InvestimentosErrorBoundary>
      <DashboardInvestimentos />
    </InvestimentosErrorBoundary>
  )
}
