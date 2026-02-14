/**
 * Componente - Gráfico de Distribuição por Tipo
 */

'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { DistribuicaoTipo } from '../types'

interface DistribuicaoChartProps {
  distribuicao: DistribuicaoTipo[]
}

export function DistribuicaoChart({ distribuicao }: DistribuicaoChartProps) {
  const formatCurrency = (value: string) => {
    const num = parseFloat(value)
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num)
  }

  // Calcular total
  const total = distribuicao.reduce((sum, d) => sum + parseFloat(d.total_investido), 0)

  // Ordenar por valor
  const sorted = [...distribuicao].sort((a, b) => 
    parseFloat(b.total_investido) - parseFloat(a.total_investido)
  )

  // Top 5
  const top5 = sorted.slice(0, 5)

  const colors = [
    'bg-blue-500',
    'bg-green-500',
    'bg-purple-500',
    'bg-orange-500',
    'bg-pink-500',
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Distribuição por Tipo</CardTitle>
        <CardDescription>
          Top 5 tipos de investimento
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {top5.map((item, index) => {
            const valor = parseFloat(item.total_investido)
            const percentual = (valor / total) * 100

            return (
              <div key={item.tipo} className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium">{item.tipo}</span>
                  <span className="text-muted-foreground">
                    {percentual.toFixed(1)}%
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full ${colors[index]}`}
                      style={{ width: `${percentual}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground min-w-[80px] text-right">
                    {formatCurrency(item.total_investido)}
                  </span>
                </div>
                <div className="text-xs text-muted-foreground">
                  {item.quantidade} {item.quantidade === 1 ? 'produto' : 'produtos'}
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
