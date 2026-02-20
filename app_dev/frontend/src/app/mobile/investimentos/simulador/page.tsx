'use client'

/**
 * Simulador de Investimentos - Mobile
 * Rota: /mobile/investimentos/simulador
 */

import { useRouter } from 'next/navigation'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { SimuladorMobile } from '@/features/investimentos/components/mobile/simulador-mobile'
import { useRequireAuth } from '@/core/hooks/use-require-auth'

export default function SimuladorInvestimentosPage() {
  const router = useRouter()
  const isAuth = useRequireAuth()

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <MobileHeader
        title="Simulador"
        subtitle="Projete a evolução do seu portfólio"
        leftAction="back"
        onBack={() => router.push('/mobile/investimentos')}
      />
      <div className="px-4 py-6">
        <SimuladorMobile />
      </div>
    </div>
  )
}
