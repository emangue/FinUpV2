'use client'

/**
 * EmptyState - UX Fundação S27
 * Estado vazio reutilizável com ícone, título, descrição e CTA
 */

import Link from 'next/link'
import { Button } from '@/components/ui/button'

export interface EmptyStateProps {
  icon: string
  title: string
  description: string
  ctaLabel: string
  ctaHref: string
  /** CTA secundário (ex: "Subir extrato primeiro") */
  ctaSecondaryLabel?: string
  ctaSecondaryHref?: string
}

export function EmptyState({
  icon,
  title,
  description,
  ctaLabel,
  ctaHref,
  ctaSecondaryLabel,
  ctaSecondaryHref,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center">
      <span className="text-5xl mb-4" role="img" aria-hidden>
        {icon}
      </span>
      <h3 className="text-lg font-semibold mb-2 text-gray-900">{title}</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-xs">{description}</p>
      <div className="flex flex-col gap-2">
        <Link href={ctaHref}>
          <Button>{ctaLabel} →</Button>
        </Link>
        {ctaSecondaryLabel && ctaSecondaryHref && (
          <Link href={ctaSecondaryHref} className="text-sm text-muted-foreground hover:underline">
            {ctaSecondaryLabel}
          </Link>
        )}
      </div>
    </div>
  )
}
