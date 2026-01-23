'use client'

import { useState, useRef, useEffect, useMemo } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface MonthTabsProps {
  selectedYear: string
  selectedMonth: string
  onMonthChange: (month: string, year: string) => void
}

const monthNames = [
  'JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
  'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ'
]

export function MonthTabs({ selectedYear, selectedMonth, onMonthChange }: MonthTabsProps) {
  // Gerar últimos 12 meses (incluindo ano)
  const months = useMemo(() => {
    const currentDate = new Date()
    const result = []
    
    // Começar de 11 meses atrás até o mês atual
    for (let i = 11; i >= 0; i--) {
      const date = new Date(currentDate)
      date.setMonth(date.getMonth() - i)
      
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = String(date.getFullYear())
      const yearShort = year.slice(-2) // Últimos 2 dígitos
      const monthName = monthNames[date.getMonth()]
      
      result.push({
        value: month,
        year: year,
        label: `${monthName} ${yearShort}`
      })
    }
    
    return result
  }, [])
  
  const scrollRef = useRef<HTMLDivElement>(null)
  const [showLeftArrow, setShowLeftArrow] = useState(false)
  const [showRightArrow, setShowRightArrow] = useState(false)

  const checkScroll = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current
      setShowLeftArrow(scrollLeft > 0)
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10)
    }
  }

  useEffect(() => {
    checkScroll()
    window.addEventListener('resize', checkScroll)
    return () => window.removeEventListener('resize', checkScroll)
  }, [])

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const scrollAmount = 200
      scrollRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      })
    }
  }

  return (
    <div className="relative">
      {/* Label Período */}
      <div className="mb-3">
        <span className="text-sm font-medium text-muted-foreground">Período:</span>
      </div>

      {/* Navegação de meses com scroll horizontal */}
      <div className="relative">
        {/* Seta esquerda */}
        {showLeftArrow && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 z-10 bg-white shadow-md rounded-full p-1 hover:bg-gray-100"
          >
            <ChevronLeft className="h-4 w-4 text-gray-600" />
          </button>
        )}

        {/* Tabs de meses */}
        <div
          ref={scrollRef}
          onScroll={checkScroll}
          className="flex gap-2 overflow-x-auto scrollbar-hide scroll-smooth px-8"
        >
          {months.map((month) => {
            const isSelected = selectedMonth === month.value && selectedYear === month.year
            
            return (
              <button
                key={`${month.year}-${month.value}`}
                onClick={() => onMonthChange(month.value, month.year)}
                className={`
                  flex-shrink-0 px-3 py-2 rounded-md font-medium text-xs transition-colors whitespace-nowrap
                  ${isSelected
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-muted-foreground hover:bg-accent hover:text-accent-foreground border'
                  }
                `}
              >
                {month.label}
              </button>
            )
          })}
        </div>

        {/* Seta direita */}
        {showRightArrow && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 z-10 bg-white shadow-md rounded-full p-1 hover:bg-gray-100"
          >
            <ChevronRight className="h-4 w-4 text-gray-600" />
          </button>
        )}
      </div>

      <style jsx global>{`
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  )
}
