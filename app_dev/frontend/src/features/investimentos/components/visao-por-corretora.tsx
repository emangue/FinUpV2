'use client'

import React, { useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Building2, TrendingUp, TrendingDown, Package, DollarSign, Percent } from 'lucide-react'
import { InvestimentoPortfolio } from '../types'

interface VisaoPorCorretoraProps {
  investimentos: InvestimentoPortfolio[]
  totalGeral: number
}

interface DadosCorretora {
  corretora: string
  quantidade: number
  totalInvestido: number
  percentual: number
  ativos: number
  inativos: number
  tipos: string[]
}

export function VisaoPorCorretora({ investimentos, totalGeral }: VisaoPorCorretoraProps) {
  // Processar dados por corretora
  const dadosCorretoras = useMemo((): DadosCorretora[] => {
    if (!investimentos || investimentos.length === 0) return []

    const corretorasMap = new Map<string, {
      produtos: InvestimentoPortfolio[]
      totalInvestido: number
      ativos: number
      inativos: number
      tipos: Set<string>
    }>()

    // Agrupar investimentos por corretora
    investimentos.forEach(inv => {
      const valorTotal = parseFloat(inv.valor_total_inicial || '0')
      
      if (!corretorasMap.has(inv.corretora)) {
        corretorasMap.set(inv.corretora, {
          produtos: [],
          totalInvestido: 0,
          ativos: 0,
          inativos: 0,
          tipos: new Set()
        })
      }

      const dados = corretorasMap.get(inv.corretora)!
      dados.produtos.push(inv)
      dados.totalInvestido += valorTotal
      dados.tipos.add(inv.tipo_investimento)
      
      if (inv.ativo) {
        dados.ativos++
      } else {
        dados.inativos++
      }
    })

    // Converter para array e calcular percentuais
    return Array.from(corretorasMap.entries())
      .map(([corretora, dados]) => ({
        corretora,
        quantidade: dados.produtos.length,
        totalInvestido: dados.totalInvestido,
        percentual: totalGeral > 0 ? (dados.totalInvestido / totalGeral) * 100 : 0,
        ativos: dados.ativos,
        inativos: dados.inativos,
        tipos: Array.from(dados.tipos).sort()
      }))
      .sort((a, b) => b.totalInvestido - a.totalInvestido) // Ordenar por valor decrescente
  }, [investimentos, totalGeral])

  // Calcular estatísticas gerais
  const stats = useMemo(() => {
    return {
      totalCorretoras: dadosCorretoras.length,
      corretoraComMaisProdutos: dadosCorretoras.length > 0 
        ? dadosCorretoras.reduce((max, curr) => curr.quantidade > max.quantidade ? curr : max)
        : null,
      corretoraComMaisPatrimonio: dadosCorretoras.length > 0
        ? dadosCorretoras.reduce((max, curr) => curr.totalInvestido > max.totalInvestido ? curr : max)
        : null,
    }
  }, [dadosCorretoras])

  // Formatar moeda
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }

  // Obter cor baseada no percentual
  const getCorPercentual = (percentual: number): string => {
    if (percentual >= 30) return 'text-red-600'
    if (percentual >= 20) return 'text-orange-600'
    if (percentual >= 10) return 'text-yellow-600'
    return 'text-green-600'
  }

  if (!investimentos || investimentos.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Visão por Corretora
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            Nenhum investimento disponível
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Card de estatísticas gerais */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total de Corretoras
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Building2 className="h-8 w-8 text-blue-600" />
              <span className="text-3xl font-bold">{stats.totalCorretoras}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Mais Produtos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col">
              <span className="text-lg font-bold truncate">
                {stats.corretoraComMaisProdutos?.corretora || 'N/A'}
              </span>
              <span className="text-sm text-muted-foreground">
                {stats.corretoraComMaisProdutos?.quantidade || 0} produtos
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Maior Patrimônio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col">
              <span className="text-lg font-bold truncate">
                {stats.corretoraComMaisPatrimonio?.corretora || 'N/A'}
              </span>
              <span className="text-sm text-muted-foreground">
                {stats.corretoraComMaisPatrimonio 
                  ? formatCurrency(stats.corretoraComMaisPatrimonio.totalInvestido)
                  : 'R$ 0,00'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabela detalhada por corretora */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Distribuição por Corretora
            </CardTitle>
            <Badge variant="outline">{dadosCorretoras.length} corretoras</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[250px]">Corretora</TableHead>
                  <TableHead className="text-center">
                    <div className="flex items-center justify-center gap-1">
                      <Package className="h-4 w-4" />
                      Produtos
                    </div>
                  </TableHead>
                  <TableHead className="text-center">Status</TableHead>
                  <TableHead className="text-center">Tipos</TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <DollarSign className="h-4 w-4" />
                      Total Investido
                    </div>
                  </TableHead>
                  <TableHead className="text-right">
                    <div className="flex items-center justify-end gap-1">
                      <Percent className="h-4 w-4" />
                      % do Total
                    </div>
                  </TableHead>
                  <TableHead className="text-center">Concentração</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dadosCorretoras.map((dado, index) => (
                  <TableRow key={dado.corretora} className={index % 2 === 0 ? 'bg-muted/50' : ''}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-muted-foreground" />
                        <span className="font-medium">{dado.corretora}</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <Badge variant="secondary">{dado.quantidade}</Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center gap-2">
                        <Badge variant="default" className="bg-green-600">
                          {dado.ativos} ativos
                        </Badge>
                        {dado.inativos > 0 && (
                          <Badge variant="secondary">
                            {dado.inativos} vencidos
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-center">
                      <div className="flex items-center justify-center gap-1 flex-wrap">
                        {dado.tipos.slice(0, 2).map(tipo => (
                          <Badge key={tipo} variant="outline" className="text-xs">
                            {tipo}
                          </Badge>
                        ))}
                        {dado.tipos.length > 2 && (
                          <Badge variant="outline" className="text-xs">
                            +{dado.tipos.length - 2}
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right font-mono font-semibold">
                      {formatCurrency(dado.totalInvestido)}
                    </TableCell>
                    <TableCell className="text-right">
                      <span className={`font-semibold ${getCorPercentual(dado.percentual)}`}>
                        {dado.percentual.toFixed(2)}%
                      </span>
                    </TableCell>
                    <TableCell className="text-center">
                      {dado.percentual >= 30 ? (
                        <div className="flex items-center justify-center gap-1 text-red-600">
                          <TrendingUp className="h-4 w-4" />
                          <span className="text-xs font-semibold">Alta</span>
                        </div>
                      ) : dado.percentual >= 20 ? (
                        <div className="flex items-center justify-center gap-1 text-orange-600">
                          <TrendingUp className="h-4 w-4" />
                          <span className="text-xs font-semibold">Média</span>
                        </div>
                      ) : (
                        <div className="flex items-center justify-center gap-1 text-green-600">
                          <TrendingDown className="h-4 w-4" />
                          <span className="text-xs font-semibold">Baixa</span>
                        </div>
                      )}
                    </TableCell>
                  </TableRow>
                ))}

                {/* Linha de totais */}
                <TableRow className="bg-muted font-bold border-t-2">
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <DollarSign className="h-4 w-4" />
                      TOTAL GERAL
                    </div>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge>{investimentos.length}</Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge variant="default" className="bg-green-600">
                      {investimentos.filter(i => i.ativo).length}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-center">
                    <Badge variant="outline">
                      {new Set(investimentos.map(i => i.tipo_investimento)).size} tipos
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {formatCurrency(totalGeral)}
                  </TableCell>
                  <TableCell className="text-right">100.00%</TableCell>
                  <TableCell className="text-center">-</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </div>

          {/* Análise de Concentração */}
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <div className="flex items-start gap-2">
              <Building2 className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold mb-1">Análise de Concentração de Risco</h4>
                <p className="text-sm text-muted-foreground">
                  {dadosCorretoras.filter(d => d.percentual >= 30).length > 0 ? (
                    <>
                      <strong className="text-red-600">Atenção:</strong> Você possui{' '}
                      <strong>{dadosCorretoras.filter(d => d.percentual >= 30).length} corretora(s)</strong> com
                      concentração acima de 30% do patrimônio. Considere diversificar para reduzir riscos.
                    </>
                  ) : dadosCorretoras.filter(d => d.percentual >= 20).length > 0 ? (
                    <>
                      <strong className="text-orange-600">Moderado:</strong> Você possui{' '}
                      <strong>{dadosCorretoras.filter(d => d.percentual >= 20).length} corretora(s)</strong> com
                      concentração entre 20-30%. Sua diversificação está adequada.
                    </>
                  ) : (
                    <>
                      <strong className="text-green-600">Excelente:</strong> Seu portfólio está bem diversificado
                      entre {stats.totalCorretoras} corretoras, sem concentração excessiva em nenhuma delas.
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
