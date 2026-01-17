'use client'

import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { TrendingUp, Calendar, Activity } from 'lucide-react'
import { RendimentoMensal } from '../types'

interface EvolucaoTemporalProps {
  timeline: RendimentoMensal[]
  cenario?: {
    rendimento_mensal: number
    aporte_mensal: number
  }
}

type PeriodoView = '3m' | '6m' | '12m' | 'all'

interface DataPoint {
  mes: number
  mesFormatado: string
  patrimonioReal: number
  patrimonioProjetado: number
}

export function EvolucaoTemporal({ timeline, cenario }: EvolucaoTemporalProps) {
  const [periodoSelecionado, setPeriodoSelecionado] = useState<PeriodoView>('6m')

  // Formatar mês YYYYMM para display
  const formatarMes = (anomes: number | string): string => {
    const anomesStr = String(anomes)
    const ano = anomesStr.substring(0, 4)
    const mes = anomesStr.substring(4, 6)
    const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    return `${meses[parseInt(mes) - 1]}/${ano.substring(2)}`
  }

  // Processar dados do timeline
  const dadosProcessados = useMemo((): DataPoint[] => {
    if (!timeline || timeline.length === 0) return []

    // Ordenar por anomes
    const sorted = [...timeline].sort((a, b) => a.anomes - b.anomes)

    // Calcular projeções baseadas no cenário
    const rendimentoMensal = cenario?.rendimento_mensal || 0.8 // 0.8% padrão
    const aporteMensal = cenario?.aporte_mensal || 5000 // R$ 5.000 padrão

    let patrimonioProjetadoAnterior = sorted.length > 0 ? parseFloat(sorted[0].patrimonio_final) : 0

    return sorted.map((item, index) => {
      const patrimonioReal = parseFloat(item.patrimonio_final)
      
      // Cálculo da projeção: saldo anterior + (saldo anterior * rendimento%) + aporte
      let patrimonioProjetado: number
      if (index === 0) {
        patrimonioProjetado = patrimonioReal // Primeiro mês = real
      } else {
        patrimonioProjetado = patrimonioProjetadoAnterior + 
                             (patrimonioProjetadoAnterior * (rendimentoMensal / 100)) + 
                             aporteMensal
        patrimonioProjetadoAnterior = patrimonioProjetado
      }

      return {
        mes: item.anomes,
        mesFormatado: formatarMes(item.anomes),
        patrimonioReal,
        patrimonioProjetado
      }
    })
  }, [timeline, cenario])

  // Filtrar por período
  const dadosFiltrados = useMemo((): DataPoint[] => {
    if (periodoSelecionado === 'all') return dadosProcessados

    const mesesMap: Record<PeriodoView, number> = {
      '3m': 3,
      '6m': 6,
      '12m': 12,
      'all': dadosProcessados.length
    }

    const qtdMeses = mesesMap[periodoSelecionado]
    return dadosProcessados.slice(-qtdMeses)
  }, [dadosProcessados, periodoSelecionado])

  // Calcular valores min e max para escala
  const { minValor, maxValor, range } = useMemo(() => {
    if (dadosFiltrados.length === 0) return { minValor: 0, maxValor: 0, range: 0 }

    const todosValores = dadosFiltrados.flatMap(d => [d.patrimonioReal, d.patrimonioProjetado])
    const min = Math.min(...todosValores)
    const max = Math.max(...todosValores)
    const buffer = (max - min) * 0.1 // 10% de margem

    return {
      minValor: min - buffer,
      maxValor: max + buffer,
      range: (max + buffer) - (min - buffer)
    }
  }, [dadosFiltrados])

  // Calcular posição Y no gráfico (0-100%)
  const calcularPosicaoY = (valor: number): number => {
    if (range === 0) return 50
    return 100 - ((valor - minValor) / range * 100)
  }

  // Gerar path SVG para linha
  const gerarPath = (dataKey: 'patrimonioReal' | 'patrimonioProjetado'): string => {
    if (dadosFiltrados.length === 0) return ''

    const width = 100 // Percentual
    const step = width / (dadosFiltrados.length - 1 || 1)

    const pontos = dadosFiltrados.map((d, i) => {
      const x = i * step
      const y = calcularPosicaoY(d[dataKey])
      return `${x},${y}`
    })

    return `M ${pontos.join(' L ')}`
  }

  // Formatar moeda
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  // Calcular variação percentual
  const calcularVariacao = (): { percentual: number; valor: number } => {
    if (dadosFiltrados.length < 2) return { percentual: 0, valor: 0 }

    const primeiro = dadosFiltrados[0].patrimonioReal
    const ultimo = dadosFiltrados[dadosFiltrados.length - 1].patrimonioReal
    const valor = ultimo - primeiro
    const percentual = (valor / primeiro) * 100

    return { percentual, valor }
  }

  const variacao = calcularVariacao()
  const ultimoDado = dadosFiltrados.length > 0 ? dadosFiltrados[dadosFiltrados.length - 1] : null
  const diferenca = ultimoDado ? ultimoDado.patrimonioProjetado - ultimoDado.patrimonioReal : 0
  const diferencaPercentual = ultimoDado && ultimoDado.patrimonioReal > 0 
    ? (diferenca / ultimoDado.patrimonioReal) * 100 
    : 0

  if (!timeline || timeline.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Evolução Temporal do Patrimônio
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Nenhum dado histórico disponível
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Evolução Temporal do Patrimônio
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Button
              variant={periodoSelecionado === '3m' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setPeriodoSelecionado('3m')}
            >
              3M
            </Button>
            <Button
              variant={periodoSelecionado === '6m' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setPeriodoSelecionado('6m')}
            >
              6M
            </Button>
            <Button
              variant={periodoSelecionado === '12m' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setPeriodoSelecionado('12m')}
            >
              12M
            </Button>
            <Button
              variant={periodoSelecionado === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setPeriodoSelecionado('all')}
            >
              Tudo
            </Button>
          </div>
        </div>

        {/* Métricas do período */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">Patrimônio Atual</span>
            <span className="text-2xl font-bold text-blue-600">
              {ultimoDado ? formatCurrency(ultimoDado.patrimonioReal) : 'N/A'}
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">Variação no Período</span>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${variacao.valor >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {variacao.valor >= 0 ? '+' : ''}{variacao.percentual.toFixed(2)}%
              </span>
              <Badge variant={variacao.valor >= 0 ? 'default' : 'destructive'}>
                {variacao.valor >= 0 ? '+' : ''}{formatCurrency(variacao.valor)}
              </Badge>
            </div>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-muted-foreground">Real vs. Projetado</span>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${diferenca >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {diferenca >= 0 ? '+' : ''}{formatCurrency(diferenca)}
              </span>
              <Badge variant={diferenca >= 0 ? 'default' : 'secondary'}>
                {diferenca >= 0 ? '+' : ''}{diferencaPercentual.toFixed(2)}%
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Gráfico SVG */}
        <div className="relative h-[300px] w-full">
          {/* Grid de fundo */}
          <svg className="absolute inset-0 w-full h-full">
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />

            {/* Linhas horizontais de referência */}
            {[0, 25, 50, 75, 100].map(percent => (
              <g key={percent}>
                <line
                  x1="0"
                  y1={`${percent}%`}
                  x2="100%"
                  y2={`${percent}%`}
                  stroke="#d1d5db"
                  strokeWidth="1"
                  strokeDasharray="4"
                />
                <text
                  x="4"
                  y={`${percent}%`}
                  dy="-4"
                  fontSize="10"
                  fill="#6b7280"
                >
                  {formatCurrency(maxValor - (range * percent / 100))}
                </text>
              </g>
            ))}

            {/* Linha Real (azul) */}
            <path
              d={gerarPath('patrimonioReal')}
              fill="none"
              stroke="#2563eb"
              strokeWidth="3"
              vectorEffect="non-scaling-stroke"
            />

            {/* Linha Projetada (verde tracejada) */}
            <path
              d={gerarPath('patrimonioProjetado')}
              fill="none"
              stroke="#16a34a"
              strokeWidth="2"
              strokeDasharray="6 4"
              vectorEffect="non-scaling-stroke"
            />

            {/* Pontos na linha real */}
            {dadosFiltrados.map((d, i) => {
              const width = 100
              const step = width / (dadosFiltrados.length - 1 || 1)
              const x = i * step
              const y = calcularPosicaoY(d.patrimonioReal)

              return (
                <circle
                  key={d.mes}
                  cx={`${x}%`}
                  cy={`${y}%`}
                  r="4"
                  fill="#2563eb"
                  stroke="white"
                  strokeWidth="2"
                />
              )
            })}
          </svg>

          {/* Labels de mês no eixo X */}
          <div className="absolute bottom-0 left-0 right-0 flex justify-between px-2 text-xs text-muted-foreground">
            {dadosFiltrados.map((d, i) => {
              // Mostrar apenas alguns labels para evitar sobreposição
              const showLabel = dadosFiltrados.length <= 6 || i % Math.ceil(dadosFiltrados.length / 6) === 0 || i === dadosFiltrados.length - 1
              
              return showLabel ? (
                <span key={d.mes} className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {d.mesFormatado}
                </span>
              ) : null
            })}
          </div>
        </div>

        {/* Legenda */}
        <div className="flex items-center justify-center gap-6 mt-8 pt-4 border-t">
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-blue-600" />
            <span className="text-sm text-muted-foreground">Patrimônio Real</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-green-600 border-t-2 border-dashed border-green-600" />
            <span className="text-sm text-muted-foreground">
              Patrimônio Projetado ({cenario?.rendimento_mensal || 0.8}% a.m. + {formatCurrency(cenario?.aporte_mensal || 5000)}/mês)
            </span>
          </div>
        </div>

        {/* Análise Rápida */}
        <div className="mt-4 p-4 bg-muted rounded-lg">
          <div className="flex items-start gap-2">
            <TrendingUp className="h-5 w-5 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold mb-1">Análise do Período</h4>
              <p className="text-sm text-muted-foreground">
                {diferenca >= 0 ? (
                  <>
                    Seu patrimônio está <strong className="text-green-600">{diferencaPercentual.toFixed(1)}% acima</strong> da projeção
                    ({formatCurrency(diferenca)} além do esperado). Continue com os aportes e rentabilidade atual!
                  </>
                ) : (
                  <>
                    Seu patrimônio está <strong className="text-orange-600">{Math.abs(diferencaPercentual).toFixed(1)}% abaixo</strong> da projeção
                    ({formatCurrency(Math.abs(diferenca))} a menos que o esperado). Considere revisar a estratégia de investimentos.
                  </>
                )}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
