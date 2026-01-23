'use client'

import { useState, useMemo } from 'react'
import { ChevronDown, Filter } from 'lucide-react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"

interface MonthFilterMobileProps {
  selectedYear: string
  selectedMonth: string
  filterType: 'all' | 'receitas' | 'despesas'
  onMonthChange: (month: string, year: string) => void
  onFilterChange: (type: 'all' | 'receitas' | 'despesas') => void
}

const monthNames = [
  'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
  'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

export function MonthFilterMobile({
  selectedYear,
  selectedMonth,
  filterType,
  onMonthChange,
  onFilterChange
}: MonthFilterMobileProps) {
  const [isOpen, setIsOpen] = useState(false)

  // Gerar últimos 12 meses
  const months = useMemo(() => {
    const currentDate = new Date()
    const result = []
    
    for (let i = 11; i >= 0; i--) {
      const date = new Date(currentDate)
      date.setMonth(date.getMonth() - i)
      
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const year = String(date.getFullYear())
      const monthName = monthNames[date.getMonth()]
      
      result.push({
        value: `${year}-${month}`,
        label: `${monthName} ${year}`,
        month,
        year
      })
    }
    
    return result
  }, [])

  const selectedMonthLabel = months.find(
    m => m.month === selectedMonth && m.year === selectedYear
  )?.label || 'Selecione'

  return (
    <div className="flex items-center gap-2">
      {/* Seletor de mês */}
      <Select
        value={`${selectedYear}-${selectedMonth}`}
        onValueChange={(value) => {
          const [year, month] = value.split('-')
          onMonthChange(month, year)
        }}
      >
        <SelectTrigger className="flex-1 bg-white">
          <SelectValue>{selectedMonthLabel}</SelectValue>
        </SelectTrigger>
        <SelectContent>
          {months.map((month) => (
            <SelectItem key={month.value} value={month.value}>
              {month.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Botão de filtros avançados */}
      <Sheet open={isOpen} onOpenChange={setIsOpen}>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="flex-shrink-0">
            <Filter className="h-4 w-4" />
          </Button>
        </SheetTrigger>
        <SheetContent side="bottom" className="h-[40vh]">
          <SheetHeader>
            <SheetTitle>Filtros</SheetTitle>
          </SheetHeader>
          
          <div className="mt-6 space-y-3">
            <Button
              variant={filterType === 'all' ? 'default' : 'outline'}
              className="w-full justify-start"
              onClick={() => {
                onFilterChange('all')
                setIsOpen(false)
              }}
            >
              Todas as Transações
            </Button>
            
            <Button
              variant={filterType === 'receitas' ? 'default' : 'outline'}
              className="w-full justify-start text-green-600"
              onClick={() => {
                onFilterChange('receitas')
                setIsOpen(false)
              }}
            >
              Apenas Receitas
            </Button>
            
            <Button
              variant={filterType === 'despesas' ? 'default' : 'outline'}
              className="w-full justify-start text-red-600"
              onClick={() => {
                onFilterChange('despesas')
                setIsOpen(false)
              }}
            >
              Apenas Despesas
            </Button>
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
}
