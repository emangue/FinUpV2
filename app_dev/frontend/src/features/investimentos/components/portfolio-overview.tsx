/**
 * Componente - Visão Geral do Portfólio
 * Otimizado com React.memo e useMemo para performance
 */

'use client'

import React, { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingUp, TrendingDown, Wallet, Package } from 'lucide-react'
import type { PortfolioResumo } from '../types'

interface PortfolioOverviewProps {
  resumo: PortfolioResumo
}

export const PortfolioOverview = React.memo(function PortfolioOverview({ resumo }: PortfolioOverviewProps) {
  // Memoização dos cálculos para evitar recálculos desnecessários
  const calculations = useMemo(() => {
    const totalInvestido = parseFloat(resumo.total_investido)
    const valorAtual = parseFloat(resumo.valor_atual)
    const rendimentoTotal = parseFloat(resumo.rendimento_total)
    const rendimentoPercentual = resumo.rendimento_percentual
    const isPositive = rendimentoTotal >= 0

    return {
      totalInvestido,
      valorAtual,
      rendimentoTotal,
      rendimentoPercentual,
      isPositive
    }
  }, [resumo.total_investido, resumo.valor_atual, resumo.rendimento_total, resumo.rendimento_percentual])

  // Memoização da função de formatação de moeda
  const formatCurrency = useMemo(() => {
    const formatter = new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    })
    return (value: number) => formatter.format(value)
  }, [])

  // Memoização da configuração dos cards
  const cards = useMemo(() => [
    {
      title: 'Total Investido',
      value: formatCurrency(calculations.totalInvestido),
      icon: Wallet,
      description: 'Valor total aplicado',
    },
    {
      title: 'Valor Atual',
      value: formatCurrency(calculations.valorAtual),
      icon: Package,
      description: 'Patrimônio atual',
    },
    {
      title: 'Rendimento Total',
      value: formatCurrency(calculations.rendimentoTotal),
      icon: calculations.isPositive ? TrendingUp : TrendingDown,
      description: `${calculations.rendimentoPercentual.toFixed(2)}% do total`,
      className: calculations.isPositive ? 'text-green-600' : 'text-red-600',
    },
    {
      title: 'Produtos Ativos',
      value: resumo.produtos_ativos.toString(),
      icon: Package,
      description: `${resumo.quantidade_produtos} produtos no total`,
    },
  ], [calculations, formatCurrency, resumo.produtos_ativos, resumo.quantidade_produtos])

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {card.title}
              </CardTitle>
              <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${card.className || ''}`}>
                {card.value}
              </div>
              <p className="text-xs text-muted-foreground">
                {card.description}
              </p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
})
