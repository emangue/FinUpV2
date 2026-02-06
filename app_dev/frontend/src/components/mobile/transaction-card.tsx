'use client'

/**
 * TransactionCard - Card de transação para mobile
 * 
 * Layout:
 * [Ícone] [Descrição]              [+/- R$ 123,45]
 *         [Grupo • Subgrupo]       [DD/MM]
 * 
 * Features:
 * - Ícone baseado em categoria
 * - Cor verde (receita) ou vermelho (despesa)
 * - Touch-friendly (mínimo 64px)
 * - Swipe opcional (integração futura)
 * - Click para detalhes
 * - Formatação pt-BR
 */

import * as React from 'react'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { cn } from '@/lib/utils'
import { CategoryIcon, type CategoryType } from './category-icon'
import { mobileTypography } from '@/config/mobile-typography'
import { mobileDimensions } from '@/config/mobile-dimensions'
import { mobileAnimations } from '@/config/mobile-animations'

interface TransactionCardProps {
  /**
   * ID da transação
   */
  id: number
  
  /**
   * Descrição da transação
   */
  description: string
  
  /**
   * Valor (positivo = receita, negativo = despesa)
   */
  amount: number
  
  /**
   * Data da transação
   */
  date: Date | string
  
  /**
   * Grupo (ex: "Casa", "Alimentação")
   */
  group?: string
  
  /**
   * Subgrupo (ex: "Aluguel", "Supermercado")
   */
  subgroup?: string
  
  /**
   * Categoria (para ícone)
   */
  category?: CategoryType
  
  /**
   * Callback ao clicar
   */
  onClick?: () => void
  
  /**
   * Classe CSS adicional
   */
  className?: string
}

export function TransactionCard({
  id,
  description,
  amount,
  date,
  group,
  subgroup,
  category,
  onClick,
  className,
}: TransactionCardProps) {
  // Determinar se é receita ou despesa
  const isIncome = amount > 0
  
  // Formatar valor
  const formatCurrency = (value: number) => {
    const formatted = new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(Math.abs(value))
    
    return isIncome ? `+${formatted}` : `-${formatted}`
  }
  
  // Formatar data
  const formatDate = (d: Date | string) => {
    if (typeof d === 'string') {
      // Se já está em formato DD/MM/YYYY, apenas pegar DD/MM
      if (d.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
        return d.substring(0, 5) // Retorna DD/MM
      }
      // Caso contrário, tentar parsear
      const dateObj = new Date(d)
      if (isNaN(dateObj.getTime())) {
        return 'Data inválida'
      }
      return format(dateObj, 'dd/MM', { locale: ptBR })
    }
    return format(d, 'dd/MM', { locale: ptBR })
  }
  
  // Montar texto do grupo
  const groupText = [group, subgroup].filter(Boolean).join(' • ')
  
  // Determinar categoria automaticamente se não fornecida
  const displayCategory = category || 'outros'
  
  return (
    <div
      className={cn(
        // Layout
        'w-full bg-white rounded-2xl p-4',
        
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
      <div className="flex items-center gap-3">
        {/* Ícone */}
        <CategoryIcon 
          category={displayCategory} 
          size={40}
          iconSize={20}
        />
        
        {/* Descrição + Grupo */}
        <div className="flex-1 min-w-0">
          <div
            className="font-semibold text-black leading-snug truncate"
            style={{
              fontSize: mobileTypography.categoryName.fontSize,
              fontWeight: mobileTypography.categoryName.fontWeight,
              lineHeight: mobileTypography.categoryName.lineHeight,
            }}
          >
            {description}
          </div>
          {groupText && (
            <div
              className="text-gray-400 leading-relaxed truncate"
              style={{
                fontSize: mobileTypography.frequency.fontSize,
                fontWeight: mobileTypography.frequency.fontWeight,
                lineHeight: mobileTypography.frequency.lineHeight,
              }}
            >
              {groupText}
            </div>
          )}
        </div>
        
        {/* Valor + Data */}
        <div className="text-right shrink-0">
          <div
            className={cn(
              'font-semibold leading-snug',
              isIncome ? 'text-green-600' : 'text-red-600'
            )}
            style={{
              fontSize: mobileTypography.amountPrimary.fontSize,
              fontWeight: mobileTypography.amountPrimary.fontWeight,
              lineHeight: mobileTypography.amountPrimary.lineHeight,
            }}
          >
            {formatCurrency(amount)}
          </div>
          <div
            className="text-gray-400 leading-relaxed"
            style={{
              fontSize: mobileTypography.amountSecondary.fontSize,
              fontWeight: mobileTypography.amountSecondary.fontWeight,
              lineHeight: mobileTypography.amountSecondary.lineHeight,
            }}
          >
            {formatDate(date)}
          </div>
        </div>
      </div>
    </div>
  )
}

/**
 * Exemplo de uso:
 * 
 * <TransactionCard
 *   id={1}
 *   description="Supermercado Extra"
 *   amount={-234.56}
 *   date={new Date()}
 *   group="Alimentação"
 *   subgroup="Supermercado"
 *   category="alimentacao"
 *   onClick={() => console.log('Transaction clicked')}
 * />
 * 
 * <TransactionCard
 *   id={2}
 *   description="Salário"
 *   amount={5000.00}
 *   date="2026-02-01"
 *   onClick={() => console.log('Income clicked')}
 * />
 */
