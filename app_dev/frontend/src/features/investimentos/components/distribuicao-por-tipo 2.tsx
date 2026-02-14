'use client'

/**
 * Componente - Distribuição por Classe de Ativo
 * 
 * Exibe:
 * - Gráfico de pizza com distribuição por tipo
 * - Tabela com percentuais e valores
 * - Métricas por classe de ativo
 */

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { PieChart, TrendingUp, TrendingDown } from 'lucide-react'
import type { DistribuicaoTipo } from '../types'

interface DistribuicaoPorTipoProps {
  distribuicao: DistribuicaoTipo[]
  totalGeral: number
}

export function DistribuicaoPorTipo({ distribuicao, totalGeral }: DistribuicaoPorTipoProps) {
  const formatCurrency = (value: string) => {
    const num = parseFloat(value)
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(num)
  }

  const getPercentual = (valor: string) => {
    if (totalGeral === 0) return 0
    return (parseFloat(valor) / totalGeral) * 100
  }

  const getTipoColor = (tipo: string) => {
    const colors: Record<string, string> = {
      'Fundo Imobiliário': 'bg-blue-500',
      'Renda Fixa': 'bg-green-500',
      'Ação': 'bg-purple-500',
      'Casa': 'bg-orange-500',
      'Apartamento': 'bg-yellow-500',
      'Previdência Privada': 'bg-indigo-500',
      'Conta Corrente': 'bg-gray-500',
      'FGTS': 'bg-pink-500',
      'Fundo de Investimento': 'bg-teal-500',
      'Automóvel': 'bg-red-500',
    }
    return colors[tipo] || 'bg-gray-500'
  }

  // Ordenar por valor (maior primeiro)
  const distribuicaoOrdenada = [...distribuicao].sort((a, b) => {
    return parseFloat(b.total_investido) - parseFloat(a.total_investido)
  })

  // Top 5 para o gráfico visual
  const top5 = distribuicaoOrdenada.slice(0, 5)
  const maxValor = distribuicaoOrdenada.length > 0 ? parseFloat(distribuicaoOrdenada[0].total_investido) : 0

  return (
    <div className="grid gap-6 md:grid-cols-2">
      {/* Card - Gráfico Visual (Barras Horizontais) */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                Top 5 Classes de Ativo
              </CardTitle>
              <CardDescription>
                Distribuição por tipo de investimento
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {top5.map((item, index) => {
              const percentual = getPercentual(item.total_investido)
              const larguraBarra = maxValor > 0 ? (parseFloat(item.total_investido) / maxValor) * 100 : 0

              return (
                <div key={item.tipo} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${getTipoColor(item.tipo)}`} />
                      <span className="font-medium">{item.tipo}</span>
                      <Badge variant="outline" className="text-xs">
                        {item.quantidade} {item.quantidade === 1 ? 'ativo' : 'ativos'}
                      </Badge>
                    </div>
                    <span className="font-semibold">{percentual.toFixed(1)}%</span>
                  </div>
                  <div className="relative h-8 bg-muted rounded-md overflow-hidden">
                    <div
                      className={`h-full ${getTipoColor(item.tipo)} opacity-80 transition-all duration-500 flex items-center justify-end pr-3`}
                      style={{ width: `${larguraBarra}%` }}
                    >
                      <span className="text-xs font-semibold text-white">
                        {formatCurrency(item.total_investido)}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>

          {distribuicao.length > 5 && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-muted-foreground text-center">
                + {distribuicao.length - 5} outras classes de ativo
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Card - Tabela Detalhada */}
      <Card>
        <CardHeader>
          <CardTitle>Detalhamento por Classe</CardTitle>
          <CardDescription>
            Valores e percentuais de todas as classes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border max-h-[400px] overflow-y-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Classe</TableHead>
                  <TableHead className="text-center">Qtd</TableHead>
                  <TableHead className="text-right">Valor</TableHead>
                  <TableHead className="text-right">%</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {distribuicaoOrdenada.map((item) => {
                  const percentual = getPercentual(item.total_investido)
                  
                  return (
                    <TableRow key={item.tipo}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-full ${getTipoColor(item.tipo)}`} />
                          <span className="font-medium">{item.tipo}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant="secondary">
                          {item.quantidade}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right font-semibold">
                        {formatCurrency(item.total_investido)}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1">
                          {percentual >= 20 ? (
                            <TrendingUp className="h-3 w-3 text-green-500" />
                          ) : percentual < 10 ? (
                            <TrendingDown className="h-3 w-3 text-muted-foreground" />
                          ) : null}
                          <span className="font-medium">{percentual.toFixed(1)}%</span>
                        </div>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </div>

          {/* Total Geral */}
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between">
              <span className="font-semibold">Total Geral:</span>
              <span className="text-lg font-bold text-primary">
                {formatCurrency(totalGeral.toString())}
              </span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Distribuído em {distribuicao.length} {distribuicao.length === 1 ? 'classe' : 'classes'} de ativo
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
