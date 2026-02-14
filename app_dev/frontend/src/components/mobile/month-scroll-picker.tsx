'use client'

/**
 * MonthScrollPicker - Scroll horizontal de meses
 * 
 * Componente crítico do Dashboard Mobile
 * Baseado no design "Trackers" do Style Guide
 * 
 * Features:
 * - Scroll horizontal suave
 * - Mês atual centralizado e destacado
 * - Touch-friendly (44px mínimo WCAG)
 * - Animações fluidas
 * - Formatação em português (Jan, Fev, Mar...)
 */

import * as React from 'react'
import { format, addMonths, subMonths, startOfMonth, isSameMonth } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import { mobileTypography } from '@/config/mobile-typography'
import { mobileDimensions } from '@/config/mobile-dimensions'
import { mobileAnimations } from '@/config/mobile-animations'

interface MonthScrollPickerProps {
  /**
   * Mês selecionado (Date object)
   */
  selectedMonth: Date
  
  /**
   * Callback quando mês é selecionado
   */
  onMonthChange: (month: Date) => void
  
  /**
   * Quantos meses mostrar antes e depois (padrão: 6)
   */
  monthsRange?: number
  
  /**
   * Classe CSS adicional
   */
  className?: string
}

export function MonthScrollPicker({
  selectedMonth,
  onMonthChange,
  monthsRange = 6,
  className
}: MonthScrollPickerProps) {
  const scrollContainerRef = React.useRef<HTMLDivElement>(null)
  const selectedMonthRef = React.useRef<HTMLButtonElement>(null)
  
  // Gerar lista de meses (antes + atual + depois)
  const months = React.useMemo(() => {
    const result: Date[] = []
    const start = subMonths(startOfMonth(new Date()), monthsRange)
    
    for (let i = 0; i <= monthsRange * 2; i++) {
      result.push(addMonths(start, i))
    }
    
    return result
  }, [monthsRange])
  
  // Scroll para o mês selecionado ao montar ou mudar seleção
  React.useEffect(() => {
    if (selectedMonthRef.current && scrollContainerRef.current) {
      const container = scrollContainerRef.current
      const button = selectedMonthRef.current
      
      // Calcular posição para centralizar
      const containerWidth = container.offsetWidth
      const buttonLeft = button.offsetLeft
      const buttonWidth = button.offsetWidth
      
      const scrollPosition = buttonLeft - (containerWidth / 2) + (buttonWidth / 2)
      
      // Scroll suave
      container.scrollTo({
        left: scrollPosition,
        behavior: 'smooth'
      })
    }
  }, [selectedMonth])
  
  return (
    <div
      className={cn(
        'w-full overflow-x-auto scrollbar-hide',
        className
      )}
      ref={scrollContainerRef}
      style={{
        // Scroll suave no iOS
        WebkitOverflowScrolling: 'touch',
        // Ocultar scrollbar
        msOverflowStyle: 'none',
        scrollbarWidth: 'none',
      }}
    >
      <div
        className="flex gap-2 px-5"
        style={{
          paddingTop: mobileDimensions.spacing.cardPadding.px,
          paddingBottom: mobileDimensions.spacing.cardPadding.px,
        }}
      >
        {months.map((month) => {
          const isSelected = isSameMonth(month, selectedMonth)
          const isCurrentMonth = isSameMonth(month, new Date())
          
          // Formatação: "Jan", "Fev", "Mar"...
          const monthLabel = format(month, 'MMM', { locale: ptBR })
            .replace('.', '') // Remover ponto (Jan. → Jan)
            .charAt(0).toUpperCase() + format(month, 'MMM', { locale: ptBR }).slice(1, 3)
          
          // Ano (SEMPRE mostrar)
          const year = format(month, 'yyyy')
          
          return (
            <button
              key={month.toISOString()}
              ref={isSelected ? selectedMonthRef : null}
              onClick={() => onMonthChange(month)}
              className={cn(
                // Base
                'flex flex-col items-center justify-center',
                'px-4 py-2 rounded-lg',
                'transition-all duration-200',
                'shrink-0', // Não encolher
                
                // Tamanho mínimo WCAG
                'min-w-[60px] min-h-[44px]',
                
                // Estados
                isSelected && [
                  'bg-black text-white',
                  'shadow-md',
                ],
                !isSelected && [
                  'bg-gray-100 text-gray-600',
                  'hover:bg-gray-200',
                  'active:bg-gray-300',
                ],
                
                // Mês atual (badge indicator)
                isCurrentMonth && !isSelected && 'ring-2 ring-blue-400'
              )}
              style={{
                ...mobileAnimations.button,
              }}
              aria-label={`${monthLabel} ${year}`}
              aria-pressed={isSelected}
            >
              {/* Mês */}
              <span
                className="font-semibold"
                style={{
                  fontSize: '15px',
                  lineHeight: '20px',
                }}
              >
                {monthLabel}
              </span>
              
              {/* Ano (SEMPRE mostrado) */}
              <span
                className={cn(
                  'text-xs',
                  isSelected ? 'text-gray-300' : 'text-gray-400'
                )}
                style={{
                  fontSize: '11px',
                  lineHeight: '14px',
                }}
              >
                {year}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
