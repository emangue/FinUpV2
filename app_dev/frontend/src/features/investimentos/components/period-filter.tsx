'use client'

/**
 * Componente - Filtro de Período
 * Permite selecionar range de datas (mês/ano)
 */

import React from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Calendar } from 'lucide-react'

interface PeriodFilterProps {
  startMonth: number
  startYear: number
  endMonth: number
  endYear: number
  onPeriodChange: (startMonth: number, startYear: number, endMonth: number, endYear: number) => void
}

export function PeriodFilter({
  startMonth,
  startYear,
  endMonth,
  endYear,
  onPeriodChange,
}: PeriodFilterProps) {
  const months = [
    'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
  ]

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 10 }, (_, i) => currentYear - 9 + i)

  const handleStartChange = (month: number, year: number) => {
    onPeriodChange(month, year, endMonth, endYear)
  }

  const handleEndChange = (month: number, year: number) => {
    onPeriodChange(startMonth, startYear, month, year)
  }

  const setPreset = (preset: 'ytd' | 'last12' | 'last6' | 'all') => {
    const now = new Date()
    const currentM = now.getMonth() + 1
    const currentY = now.getFullYear()

    switch (preset) {
      case 'ytd':
        onPeriodChange(1, currentY, currentM, currentY)
        break
      case 'last12':
        const start12 = new Date(now.getFullYear(), now.getMonth() - 11, 1)
        onPeriodChange(start12.getMonth() + 1, start12.getFullYear(), currentM, currentY)
        break
      case 'last6':
        const start6 = new Date(now.getFullYear(), now.getMonth() - 5, 1)
        onPeriodChange(start6.getMonth() + 1, start6.getFullYear(), currentM, currentY)
        break
      case 'all':
        onPeriodChange(5, 2024, currentM, currentY) // Início dos dados: maio/2024
        break
    }
  }

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Presets rápidos */}
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Período:</span>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPreset('last6')}
              >
                Últimos 6 meses
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPreset('last12')}
              >
                Últimos 12 meses
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPreset('ytd')}
              >
                Ano atual
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPreset('all')}
              >
                Todo período
              </Button>
            </div>
          </div>

          {/* Seleção manual */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">De:</span>
              <select
                value={startMonth}
                onChange={(e) => handleStartChange(Number(e.target.value), startYear)}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {months.map((month, idx) => (
                  <option key={idx} value={idx + 1}>
                    {month}
                  </option>
                ))}
              </select>
              <select
                value={startYear}
                onChange={(e) => handleStartChange(startMonth, Number(e.target.value))}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>

            <span className="text-muted-foreground">→</span>

            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Até:</span>
              <select
                value={endMonth}
                onChange={(e) => handleEndChange(Number(e.target.value), endYear)}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {months.map((month, idx) => (
                  <option key={idx} value={idx + 1}>
                    {month}
                  </option>
                ))}
              </select>
              <select
                value={endYear}
                onChange={(e) => handleEndChange(endMonth, Number(e.target.value))}
                className="rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                {years.map((year) => (
                  <option key={year} value={year}>
                    {year}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
