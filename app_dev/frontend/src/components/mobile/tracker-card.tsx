'use client'

/**
 * TrackerCard - Card de categoria com progress bar
 * 
 * Baseado exatamente no design "Trackers" do Style Guide:
 * 
 * Layout:
 * [Ícone 48px] [Nome categoria]           [R$ 1.234,56]
 *              [Frequência]                [R$ 5.000,00]
 *              [━━━━━━━━━━━━━━━━━] Progress 6px
 * 
 * Features:
 * - Integra CategoryIcon + ProgressBar
 * - Formatação de moeda pt-BR
 * - Touch-friendly (mínimo 64px altura)
 * - Border radius 16px
 * - Shadow sutil
 * - Animação no hover/active
 * - Acessibilidade completa
 */

import * as React from 'react'
import { cn } from '@/lib/utils'
import { CategoryIcon, type CategoryType } from './category-icon'
import { ProgressBar } from './progress-bar'
import { mobileTypography } from '@/config/mobile-typography'
import { mobileDimensions } from '@/config/mobile-dimensions'
import { mobileAnimations } from '@/config/mobile-animations'

// Re-export CategoryType para uso externo
export type { CategoryType }

interface TrackerCardProps {
  /**
   * Categoria (casa, alimentacao, compras, etc)
   */
  category: CategoryType
  
  /**
   * Nome da categoria (ex: "Casa", "Alimentação")
   */
  categoryName: string
  
  /**
   * Frequência (ex: "Mensal", "Anual", "Semanal")
   */
  frequency?: string
  
  /**
   * Valor gasto até o momento
   */
  spent: number
  
  /**
   * Valor do orçamento total
   */
  budget: number
  
  /**
   * Callback ao clicar no card
   */
  onClick?: () => void
  
  /**
   * Classe CSS adicional
   */
  className?: string
}

export function TrackerCard({
  category,
  categoryName,
  frequency = 'Mensal',
  spent,
  budget,
  onClick,
  className,
}: TrackerCardProps) {
  // Calcular percentual
  const percentage = budget > 0 ? (spent / budget) * 100 : 0
  
  // Formatação de moeda
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(value)
  }
  
  return (
    <div
      className={cn(
        // Layout
        'w-full bg-white rounded-2xl p-5',
        
        // Visual
        'shadow-sm',
        'border border-gray-100',
        
        // Interação
        onClick && [
          'cursor-pointer',
          'active:scale-[0.98]',
          'transition-transform duration-150',
        ],
        
        className
      )}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      style={{
        minHeight: mobileDimensions.touchTarget,
        borderRadius: mobileDimensions.borderRadius.card,
        ...mobileAnimations.card,
      }}
    >
      {/* Header: Ícone + Categoria + Valores */}
      <div className="flex items-start gap-3 mb-3">
        {/* Ícone */}
        <CategoryIcon category={category} />
        
        {/* Categoria + Frequência */}
        <div className="flex-1 min-w-0">
          <div
            className="font-semibold text-black leading-snug"
            style={{
              fontSize: mobileTypography.categoryName.fontSize,
              fontWeight: mobileTypography.categoryName.fontWeight,
              lineHeight: mobileTypography.categoryName.lineHeight,
            }}
          >
            {categoryName}
          </div>
          <div
            className="text-gray-400 leading-relaxed"
            style={{
              fontSize: mobileTypography.frequency.fontSize,
              fontWeight: mobileTypography.frequency.fontWeight,
              lineHeight: mobileTypography.frequency.lineHeight,
            }}
          >
            {frequency}
          </div>
        </div>
        
        {/* Valores (Gasto / Orçamento) */}
        <div className="text-right">
          <div
            className="font-semibold text-black leading-snug"
            style={{
              fontSize: mobileTypography.amountPrimary.fontSize,
              fontWeight: mobileTypography.amountPrimary.fontWeight,
              lineHeight: mobileTypography.amountPrimary.lineHeight,
            }}
          >
            {formatCurrency(spent)}
          </div>
          <div
            className="text-gray-400 leading-relaxed"
            style={{
              fontSize: mobileTypography.amountSecondary.fontSize,
              fontWeight: mobileTypography.amountSecondary.fontWeight,
              lineHeight: mobileTypography.amountSecondary.lineHeight,
            }}
          >
            {formatCurrency(budget)}
          </div>
        </div>
      </div>
      
      {/* Progress Bar */}
      <ProgressBar
        percentage={percentage}
        category={category}
        showWarning
        showDanger
        ariaLabel={`${categoryName}: ${Math.round(percentage)}% do orçamento utilizado`}
      />
    </div>
  )
}

/**
 * Exemplo de uso:
 * 
 * <TrackerCard
 *   category="casa"
 *   categoryName="Casa"
 *   frequency="Mensal"
 *   spent={1234.56}
 *   budget={5000.00}
 *   onClick={() => console.log('Card clicado')}
 * />
 * 
 * <TrackerCard
 *   category="alimentacao"
 *   categoryName="Alimentação"
 *   spent={3500}
 *   budget={3000}
 * />
 */
