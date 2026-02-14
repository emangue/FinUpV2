'use client'

/**
 * CategoryIcon - Ícone circular colorido de categoria
 * 
 * Baseado no design "Trackers" do Style Guide:
 * - Círculo de 48px com ícone de 24px
 * - Cores extraídas da imagem de referência
 * - 6 categorias principais: casa, alimentacao, compras, transporte, contas, lazer
 * 
 * Features:
 * - Ícones Lucide React
 * - Paleta de cores oficial do projeto
 * - Tamanho touch-friendly (48px)
 * - Acessibilidade (aria-label)
 */

import * as React from 'react'
import { 
  Home, 
  UtensilsCrossed, 
  ShoppingBag, 
  Car, 
  FileText, 
  PartyPopper,
  DollarSign
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { categoryColors } from '@/config/mobile-colors'
import type { CategoryColor } from '@/config/mobile-colors'
import { mobileDimensions } from '@/config/mobile-dimensions'

// Mapa de ícones por categoria
const CATEGORY_ICONS = {
  casa: Home,
  alimentacao: UtensilsCrossed,
  compras: ShoppingBag,
  transporte: Car,
  contas: FileText,
  lazer: PartyPopper,
  outros: DollarSign,
} as const

export type CategoryType = keyof typeof CATEGORY_ICONS

interface CategoryIconProps {
  /**
   * Tipo de categoria (casa, alimentacao, compras, etc)
   */
  category: CategoryType
  
  /**
   * Tamanho do círculo em pixels (padrão: 48px)
   */
  size?: number
  
  /**
   * Tamanho do ícone em pixels (padrão: 24px)
   */
  iconSize?: number
  
  /**
   * Classe CSS adicional
   */
  className?: string
  
  /**
   * Label de acessibilidade (padrão: nome da categoria)
   */
  ariaLabel?: string
}

export function CategoryIcon({
  category,
  size = 48,
  iconSize = 24,
  className,
  ariaLabel,
}: CategoryIconProps) {
  // Buscar ícone e cor da categoria
  const Icon = CATEGORY_ICONS[category] || CATEGORY_ICONS.outros
  const categoryToColor: Record<CategoryType, CategoryColor> = {
    casa: 'purple',
    alimentacao: 'blue',
    compras: 'pink',
    transporte: 'stone',
    contas: 'amber',
    lazer: 'green',
    outros: 'stone',
  }
  const colors = categoryColors[categoryToColor[category] || 'stone']
  
  return (
    <div
      className={cn(
        'flex items-center justify-center',
        'rounded-full',
        'shrink-0',
        className
      )}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        backgroundColor: colors.bg,
      }}
      role="img"
      aria-label={ariaLabel || category}
    >
      <Icon
        size={iconSize}
        style={{ color: colors.icon }}
        strokeWidth={2}
      />
    </div>
  )
}

/**
 * Exemplo de uso:
 * 
 * <CategoryIcon category="casa" />
 * <CategoryIcon category="alimentacao" size={64} iconSize={32} />
 * <CategoryIcon category="compras" ariaLabel="Categoria de Compras" />
 */
