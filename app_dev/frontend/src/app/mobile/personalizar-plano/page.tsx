'use client'

/**
 * Personalizar Plano - Simulador de Aposentadoria
 * Sprint H: create (?id=) e edit (?id=123)
 */

import { useSearchParams } from 'next/navigation'
import { PersonalizarPlanoLayout } from '@/features/plano-aposentadoria/components/PersonalizarPlanoLayout'

export default function PersonalizarPlanoPage() {
  const searchParams = useSearchParams()
  const idParam = searchParams.get('id')
  const cenarioId = idParam ? parseInt(idParam, 10) : undefined

  return <PersonalizarPlanoLayout cenarioId={Number.isNaN(cenarioId as number) ? undefined : cenarioId} />
}
