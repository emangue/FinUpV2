/**
 * Componente - Timeline com Indicadores
 */

'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ArrowUpIcon, ArrowDownIcon } from 'lucide-react'
import type { RendimentoMensal } from '../types'

interface TimelineIndicatorsProps {
  rendimentos: RendimentoMensal[]
}

export function TimelineIndicators({ rendimentos }: TimelineIndicatorsProps) {
  const formatCurrency = (value: string) => {
    const num = parseFloat(value)
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num)
  }

  const formatMonth = (anomes: number) => {
    const mes = anomes % 100
    const ano = Math.floor(anomes / 100)
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return `${meses[mes - 1]}/${ano}`
  }

  // Últimos 6 meses
  const ultimos6 = rendimentos.slice(-6)

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Rendimento Mensal */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            📈 Rendimento Mensal
          </CardTitle>
          <CardDescription>
            Evolução dos últimos 6 meses
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between space-x-2 overflow-x-auto">
            {ultimos6.map((r) => {
              const valor = parseFloat(r.rendimento_mes)
              const isPositive = valor >= 0
              
              return (
                <div key={r.anomes} className="flex flex-col items-center min-w-[80px]">
                  <span className="text-xs text-muted-foreground mb-1">
                    {formatMonth(r.anomes)}
                  </span>
                  <div className={`flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                    {isPositive ? (
                      <ArrowUpIcon className="h-3 w-3" />
                    ) : (
                      <ArrowDownIcon className="h-3 w-3" />
                    )}
                    <span className="text-sm font-semibold ml-1">
                      {formatCurrency(r.rendimento_mes)}
                    </span>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Saldo dos Investimentos */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm font-medium">
            🏦 Saldo dos Investimentos
          </CardTitle>
          <CardDescription>
            Patrimônio ao longo do tempo
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between space-x-2 overflow-x-auto">
            {ultimos6.map((r) => {
              return (
                <div key={r.anomes} className="flex flex-col items-center min-w-[80px]">
                  <span className="text-xs text-muted-foreground mb-1">
                    {formatMonth(r.anomes)}
                  </span>
                  <span className="text-sm font-semibold text-blue-600">
                    {formatCurrency(r.patrimonio_final)}
                  </span>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
