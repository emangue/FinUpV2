'use client'

/**
 * YearScrollPicker - Scroll horizontal de anos
 * Usado no modo YTD e Ano do dashboard
 */

import * as React from 'react'
import { cn } from '@/lib/utils'
import { mobileDimensions } from '@/config/mobile-dimensions'
import { mobileAnimations } from '@/config/mobile-animations'

interface YearScrollPickerProps {
  years: number[]
  selectedYear: number
  onYearChange: (year: number) => void
  className?: string
}

export function YearScrollPicker({
  years,
  selectedYear,
  onYearChange,
  className,
}: YearScrollPickerProps) {
  const scrollContainerRef = React.useRef<HTMLDivElement>(null)
  const selectedRef = React.useRef<HTMLButtonElement>(null)

  React.useEffect(() => {
    if (selectedRef.current && scrollContainerRef.current) {
      const container = scrollContainerRef.current
      const button = selectedRef.current
      const scrollPosition = button.offsetLeft - (container.offsetWidth / 2) + (button.offsetWidth / 2)
      container.scrollTo({ left: scrollPosition, behavior: 'smooth' })
    }
  }, [selectedYear])

  if (!years.length) return null

  return (
    <div
      ref={scrollContainerRef}
      className={cn('w-full overflow-x-auto scrollbar-hide', className)}
      style={{ WebkitOverflowScrolling: 'touch', msOverflowStyle: 'none', scrollbarWidth: 'none' }}
    >
      <div className="flex gap-2 px-5" style={{ paddingTop: mobileDimensions.spacing.cardPadding.px, paddingBottom: mobileDimensions.spacing.cardPadding.px }}>
        {years.map((y) => {
          const isSelected = y === selectedYear
          return (
            <button
              key={y}
              ref={isSelected ? selectedRef : null}
              onClick={() => onYearChange(y)}
              className={cn(
                'px-4 py-2 rounded-lg shrink-0 min-w-[60px] min-h-[44px] transition-all duration-200',
                isSelected ? 'bg-black text-white shadow-md' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              )}
              style={mobileAnimations.button}
              aria-label={`Ano ${y}`}
              aria-pressed={isSelected}
            >
              <span className="font-semibold" style={{ fontSize: '15px' }}>{y}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
