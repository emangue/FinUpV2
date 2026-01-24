'use client'

import { useMemo } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

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
        value: `${year}-${month}`,
        label: `${monthName} ${yearShort}`,
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
    <div>
      {/* Label Período */}
      <div className="mb-3">
        <span className="text-sm font-medium text-muted-foreground">Período:</span>
      </div>

      {/* Dropdown de seleção de mês */}
      <Select
        value={`${selectedYear}-${selectedMonth}`}
        onValueChange={(value) => {
          const [year, month] = value.split('-')
          onMonthChange(month, year)
        }}
      >
        <SelectTrigger className="w-full bg-white">
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
    </div>
  )
}
