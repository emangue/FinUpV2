'use client'

/**
 * ProgressBar - Barra de progresso standalone
 * 
 * Baseado no design "Trackers" do Style Guide:
 * - Altura de 6px
 * - Cor de progresso baseada na categoria
 * - Background cinza claro
 * - Border radius de 3px (metade da altura)
 * 
 * Features:
 * - Percentual de 0-100%
 * - Cores automáticas por categoria
 * - Animação suave
 * - Acessibilidade (role="progressbar")
 * - Estados de warning (>80%) e danger (>100%)
 */

import * as React from 'react'
import { cn } from '@/lib/utils'
import { categoryColors } from '@/config/mobile-colors'
import type { CategoryColor } from '@/config/mobile-colors'
import type { CategoryType } from '@/components/mobile/category-icon'

const categoryToColor: Record<CategoryType, CategoryColor> = {
  casa: 'purple',
  alimentacao: 'blue',
  compras: 'pink',
  transporte: 'stone',
  contas: 'amber',
  lazer: 'green',
  outros: 'stone',
}
import { mobileDimensions } from '@/config/mobile-dimensions'
import { mobileAnimations } from '@/config/mobile-animations'

interface ProgressBarProps {
  /**
   * Percentual de progresso (0-100+)
   */
  percentage: number
  
  /**
   * Categoria (para cor automática)
   */
  category?: CategoryType
  
  /**
   * Cor customizada (sobrescreve categoria)
   */
  color?: string
  
  /**
   * Altura da barra em pixels (padrão: 6px)
   */
  height?: number
  
  /**
   * Mostrar warning (amarelo) quando >= 80%
   */
  showWarning?: boolean
  
  /**
   * Mostrar danger (vermelho) quando > 100%
   */
  showDanger?: boolean
  
  /**
   * Classe CSS adicional
   */
  className?: string
  
  /**
   * Label de acessibilidade
   */
  ariaLabel?: string
}

export function ProgressBar({
  percentage,
  category,
  color,
  height = 6,
  showWarning = true,
  showDanger = true,
  className,
  ariaLabel,
}: ProgressBarProps) {
  // Limitar percentual entre 0-100 para display (mas permitir >100 para cálculo)
  const displayPercentage = Math.min(percentage, 100)
  const isOverBudget = percentage > 100
  const isWarning = percentage >= 80 && percentage <= 100
  
  // Determinar cor da barra
  let barColor = color
  
  if (!barColor) {
    if (showDanger && isOverBudget) {
      barColor = '#EF4444' // red-500
    } else if (showWarning && isWarning) {
      barColor = '#F59E0B' // amber-500
    } else if (category) {
      barColor = categoryColors[categoryToColor[category] || 'stone'].progress
    } else {
      barColor = '#3B82F6' // blue-500 (padrão)
    }
  }
  
  return (
    <div
      className={cn('w-full overflow-hidden', className)}
      style={{
        height: `${height}px`,
        backgroundColor: '#F3F4F6', // gray-100
        borderRadius: `${height / 2}px`,
      }}
      role="progressbar"
      aria-valuenow={Math.round(percentage)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={ariaLabel || `${Math.round(percentage)}% completo`}
    >
      <div
        className="h-full transition-all duration-300 ease-out"
        style={{
          width: `${displayPercentage}%`,
          backgroundColor: barColor,
          borderRadius: `${height / 2}px`,
        }}
      />
    </div>
  )
}

/**
 * Exemplo de uso:
 * 
 * <ProgressBar percentage={45} category="casa" />
 * <ProgressBar percentage={85} category="alimentacao" showWarning />
 * <ProgressBar percentage={120} category="compras" showDanger />
 * <ProgressBar percentage={60} color="#FF6B6B" height={8} />
 */
