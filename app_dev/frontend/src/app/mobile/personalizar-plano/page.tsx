'use client'

/**
 * Personalizar Plano - Simulador de Aposentadoria
 * Sprint H: create (?id=) e edit (?id=123)
 */

import { Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { PersonalizarPlanoLayout } from '@/features/plano-aposentadoria/components/PersonalizarPlanoLayout'

function PersonalizarPlanoContent() {
  const searchParams = useSearchParams()
  const idParam = searchParams.get('id')
  const cenarioId = idParam ? parseInt(idParam, 10) : undefined

  return <PersonalizarPlanoLayout cenarioId={Number.isNaN(cenarioId as number) ? undefined : cenarioId} />
}

export default function PersonalizarPlanoPage() {
  return (
    <Suspense fallback={<div className="flex min-h-[200px] items-center justify-center">Carregando...</div>}>
      <PersonalizarPlanoContent />
    </Suspense>
  )
}
