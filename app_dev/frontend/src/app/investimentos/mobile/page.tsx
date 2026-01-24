/**
 * Página - Investimentos Mobile
 */

import { DashboardInvestimentosMobile } from '@/features/investimentos/components/mobile/dashboard-investimentos-mobile'
import { InvestimentosErrorBoundary } from '@/features/investimentos/components/error-boundary'

export default function InvestimentosMobilePage() {
  return (
    <InvestimentosErrorBoundary>
      <DashboardInvestimentosMobile />
    </InvestimentosErrorBoundary>
  )
}
