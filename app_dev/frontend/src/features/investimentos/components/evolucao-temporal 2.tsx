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

    // Começar com o patrimônio real de maio/24 (primeiro mês)
    let patrimonioProjetadoAnterior = sorted.length > 0 ? parseFloat(sorted[0].patrimonio_final) : 0

    return sorted.map((item, index) => {
      const patrimonioReal = parseFloat(item.patrimonio_final)
      
      // Cálculo da projeção: saldo anterior + (saldo anterior * rendimento%) + aporte
      let patrimonioProjetado: number
      if (index === 0) {
        // Primeiro mês = patrimônio real inicial
        patrimonioProjetado = patrimonioReal
      } else {
        // Meses seguintes: aplicar rendimento + aporte sobre o valor projetado anterior
        patrimonioProjetado = patrimonioProjetadoAnterior + 
                             (patrimonioProjetadoAnterior * (rendimentoMensal / 100)) + 
                             aporteMensal
      }
      
      patrimonioProjetadoAnterior = patrimonioProjetado

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

  // Constantes para dimensões do gráfico
  const GRAPH_PADDING_LEFT = 80 // Espaço para legendas do eixo Y
  const GRAPH_PADDING_RIGHT = 20
  const GRAPH_PADDING_BOTTOM = 30 // Espaço para labels do eixo X
  const GRAPH_WIDTH = 1000
  const GRAPH_HEIGHT = 300
  const GRAPH_TOTAL_HEIGHT = GRAPH_HEIGHT + GRAPH_PADDING_BOTTOM
  const GRAPH_AREA_WIDTH = GRAPH_WIDTH - GRAPH_PADDING_LEFT - GRAPH_PADDING_RIGHT

  // Gerar path SVG para linha
  const gerarPath = (dataKey: 'patrimonioReal' | 'patrimonioProjetado'): string => {
    if (dadosFiltrados.length === 0) return ''

    const step = GRAPH_AREA_WIDTH / (dadosFiltrados.length - 1 || 1)

    const pontos = dadosFiltrados.map((d, i) => {
      const x = GRAPH_PADDING_LEFT + (i * step)
      const y = (calcularPosicaoY(d[dataKey]) / 100) * GRAPH_HEIGHT
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

  // Formatar valores em K/M para labels do eixo
  const formatAxisValue = (value: number): string => {
    const absValue = Math.abs(value)
    if (absValue >= 1000000) {
      return `R$ ${(value / 1000000).toFixed(1)}M`
    } else if (absValue >= 1000) {
      return `R$ ${(value / 1000).toFixed(0)}k`
    }
    return `R$ ${value.toFixed(0)}`
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
              <span className={`text-2xl font-bold ${diferenca >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                {diferenca >= 0 ? '-' : '+'}{formatCurrency(Math.abs(diferenca))}
              </span>
              <Badge variant={diferenca >= 0 ? 'secondary' : 'default'}>
                {diferenca >= 0 ? '-' : '+'}{Math.abs(diferencaPercentual).toFixed(2)}%
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {/* Gráfico SVG */}
        <div className="relative h-[320px] w-full pb-8">
          {/* Grid de fundo */}
          <svg 
            className="absolute inset-0 w-full h-full" 
            viewBox={`0 0 ${GRAPH_WIDTH} ${GRAPH_TOTAL_HEIGHT}`}
            preserveAspectRatio="xMidYMid meet"
          >
            <defs>
              <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
                <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#e5e7eb" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect x={GRAPH_PADDING_LEFT} width={GRAPH_AREA_WIDTH} height="100%" fill="url(#grid)" />

            {/* Linhas horizontais de referência */}
            {[0, 25, 50, 75, 100].map(percent => {
              const y = (percent / 100) * GRAPH_HEIGHT
              const valor = maxValor - (range * percent / 100)
              return (
                <g key={percent}>
                  <line
                    x1={GRAPH_PADDING_LEFT}
                    y1={y}
                    x2={GRAPH_WIDTH - GRAPH_PADDING_RIGHT}
                    y2={y}
                    stroke="#d1d5db"
                    strokeWidth="1"
                    strokeDasharray="4"
                    vectorEffect="non-scaling-stroke"
                  />
                  <text
                    x={GRAPH_PADDING_LEFT - 8}
                    y={y}
                    dy="4"
                    fontSize="11"
                    fill="#6b7280"
                    textAnchor="end"
                  >
                    {formatAxisValue(valor)}
                  </text>
                </g>
              )
            })}

            {/* Linha Real (azul sólida) */}
            <path
              d={gerarPath('patrimonioReal')}
              fill="none"
              stroke="#2563eb"
              strokeWidth="3"
              vectorEffect="non-scaling-stroke"
            />

            {/* Pontos azuis na linha real com labels */}
            {dadosFiltrados.map((d, i) => {
              const step = GRAPH_AREA_WIDTH / (dadosFiltrados.length - 1 || 1)
              const x = GRAPH_PADDING_LEFT + (i * step)
              const y = (calcularPosicaoY(d.patrimonioReal) / 100) * GRAPH_HEIGHT

              // Mostrar label a cada 2 pontos para não poluir
              const totalPontos = dadosFiltrados.length
              let intervaloLabel = 2
              if (totalPontos > 15) intervaloLabel = 3
              if (totalPontos > 20) intervaloLabel = 4
              const showLabel = i % intervaloLabel === 0 || i === dadosFiltrados.length - 1

              return (
                <g key={`real-${d.mes}`}>
                  <circle
                    cx={x}
                    cy={y}
                    r="3"
                    fill="#2563eb"
                    stroke="white"
                    strokeWidth="2"
                    vectorEffect="non-scaling-stroke"
                  />
                  {showLabel && (
                    <text
                      x={x}
                      y={y - 10}
                      fontSize="10"
                      fill="#2563eb"
                      fontWeight="600"
                      textAnchor="middle"
                    >
                      {formatAxisValue(d.patrimonioReal)}
                    </text>
                  )}
                </g>
              )
            })}

            {/* Pontos verdes na projeção com labels */}
            {dadosFiltrados.map((d, i) => {
              const step = GRAPH_AREA_WIDTH / (dadosFiltrados.length - 1 || 1)
              const x = GRAPH_PADDING_LEFT + (i * step)
              const y = (calcularPosicaoY(d.patrimonioProjetado) / 100) * GRAPH_HEIGHT

              // Mostrar label a cada 2 pontos
              const totalPontos = dadosFiltrados.length
              let intervaloLabel = 2
              if (totalPontos > 15) intervaloLabel = 3
              if (totalPontos > 20) intervaloLabel = 4
              const showLabel = i % intervaloLabel === 0 || i === dadosFiltrados.length - 1

              return (
                <g key={`proj-${d.mes}`}>
                  <circle
                    cx={x}
                    cy={y}
                    r="4"
                    fill="#16a34a"
                    stroke="white"
                    strokeWidth="2"
                    vectorEffect="non-scaling-stroke"
                  />
                  {showLabel && (
                    <text
                      x={x}
                      y={y - 10}
                      fontSize="10"
                      fill="#16a34a"
                      fontWeight="600"
                      textAnchor="middle"
                    >
                      {formatAxisValue(d.patrimonioProjetado)}
                    </text>
                  )}
                </g>
              )
            })}
            {/* Labels de mês no eixo X (dentro do SVG) */}
            {dadosFiltrados.map((d, i) => {
              // Calcular quantos labels mostrar baseado no tamanho
              const totalPontos = dadosFiltrados.length
              let intervalo = 1
              if (totalPontos > 12) intervalo = Math.ceil(totalPontos / 8)
              else if (totalPontos > 6) intervalo = 2
              
              const showLabel = i % intervalo === 0 || i === dadosFiltrados.length - 1
              
              if (!showLabel) return null
              
              const step = GRAPH_AREA_WIDTH / (dadosFiltrados.length - 1 || 1)
              const x = GRAPH_PADDING_LEFT + (i * step)
              
              return (
                <text
                  key={`label-${d.mes}`}
                  x={x}
                  y={GRAPH_HEIGHT + 20}
                  fontSize="11"
                  fill="#6b7280"
                  textAnchor="middle"
                >
                  {d.mesFormatado}
                </text>
              )
            })}
          </svg>
        </div>

        {/* Legenda */}
        <div className="flex items-center justify-center gap-6 mt-8 pt-4 border-t">
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-blue-600" />
            <span className="text-sm text-muted-foreground">Patrimônio Real</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-green-600" />
              <div className="w-1.5 h-1.5 rounded-full bg-green-600" />
              <div className="w-1.5 h-1.5 rounded-full bg-green-600" />
            </div>
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
