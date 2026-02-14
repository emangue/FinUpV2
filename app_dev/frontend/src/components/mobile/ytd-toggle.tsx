'use client'

/**
 * YTDToggle - Toggle entre visualização Mensal e Anual (YTD)
 * 
 * Componente para alternar entre:
 * - Mês: Dados do mês selecionado
 * - Ano: Year-to-Date (Janeiro até mês atual)
 * 
 * Baseado no design "Trackers" do Style Guide
 * 
 * Features:
 * - Estados visuais claros
 * - Touch-friendly (44px mínimo WCAG)
 * - Animação suave de transição
 * - Acessibilidade completa
 */

import * as React from 'react'
import { cn } from '@/lib/utils'
import { mobileTypography } from '@/config/mobile-typography'
import { mobileDimensions } from '@/config/mobile-dimensions'
import { mobileAnimations } from '@/config/mobile-animations'

export type YTDToggleValue = 'month' | 'ytd'

interface YTDToggleProps {
  /**
   * Valor atual ('month' ou 'ytd')
   */
  value: YTDToggleValue
  
  /**
   * Callback quando valor muda
   */
  onChange: (value: YTDToggleValue) => void
  
  /**
   * Labels customizados (opcional)
   */
  labels?: {
    month: string
    ytd: string
  }
  
  /**
   * Classe CSS adicional
   */
  className?: string
}

export function YTDToggle({
  value,
  onChange,
  labels = {
    month: 'Mês',
    ytd: 'Ano'
  },
  className
}: YTDToggleProps) {
  return (
    <div
      className={cn(
        'inline-flex items-center',
        'bg-gray-100 rounded-lg p-1',
        className
      )}
      role="tablist"
      aria-label="Período de visualização"
      style={{
        minHeight: mobileDimensions.sizes.touchTargetMinimum.px,
      }}
    >
      {/* Botão MÊS */}
      <button
        role="tab"
        aria-selected={value === 'month'}
        aria-controls="dashboard-content"
        onClick={() => onChange('month')}
        className={cn(
          // Base
          'px-4 py-2 rounded-md',
          'font-semibold text-sm',
          'transition-all duration-200',
          'min-w-[60px] min-h-[36px]', // Touch-friendly
          
          // Estados
          value === 'month' ? [
            'bg-white text-black',
            'shadow-sm',
          ] : [
            'bg-transparent text-gray-500',
            'hover:text-gray-700',
          ]
        )}
        style={{
          fontSize: mobileTypography.frequency.fontSize,
          fontWeight: value === 'month' ? 600 : 500,
          lineHeight: mobileTypography.frequency.lineHeight,
          ...mobileAnimations.button,
        }}
      >
        {labels.month}
      </button>
      
      {/* Botão ANO (YTD) */}
      <button
        role="tab"
        aria-selected={value === 'ytd'}
        aria-controls="dashboard-content"
        onClick={() => onChange('ytd')}
        className={cn(
          // Base
          'px-4 py-2 rounded-md',
          'font-semibold text-sm',
          'transition-all duration-200',
          'min-w-[60px] min-h-[36px]', // Touch-friendly
          
          // Estados
          value === 'ytd' ? [
            'bg-white text-black',
            'shadow-sm',
          ] : [
            'bg-transparent text-gray-500',
            'hover:text-gray-700',
          ]
        )}
        style={{
          fontSize: mobileTypography.frequency.fontSize,
          fontWeight: value === 'ytd' ? 600 : 500,
          lineHeight: mobileTypography.frequency.lineHeight,
          ...mobileAnimations.button,
        }}
      >
        {labels.ytd}
      </button>
    </div>
  )
}
