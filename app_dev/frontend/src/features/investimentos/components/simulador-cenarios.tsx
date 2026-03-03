'use client'

/**
 * Componente de Simulador de Cenários de Investimentos
 * 
 * Permite simular evolução do portfólio com diferentes parâmetros:
 * - Taxa de rendimento esperada
 * - Aportes mensais
 * - Período de projeção
 * 
 * Exibe 3 linhas no gráfico:
 * 1. Patrimônio Estimado (projeção)
 * 2. Patrimônio Real (dados históricos)
 * 3. Curto Prazo (próximos meses com projeções conservadoras)
 */

import React, { useState, useCallback } from 'react'
import { logger } from '@/lib/logger'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Calculator, TrendingUp, Calendar, DollarSign, Save, Play, Plus, Trash2, LineChart, Info } from 'lucide-react'
import { LineChart as RechartsLineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'
import { simularCenarioPersonalizado, criarCenario } from '../services/investimentos-api'
import { apiGet } from '@/core/config/api.config'  // ✅ FASE 1 - Autenticação automática
import type { SimulacaoCenario, ParametrosSimulacao } from '../types'

interface AporteExtraordinario {
  id: string
  mesAno: number  // 1-12 (Janeiro a Dezembro)
  valor: number
  descricao: string
  recorrencia: 'unico' | 'trimestral' | 'semestral' | 'anual'
  evoluir: boolean  // Se o valor evolui ao longo do tempo
  evolucaoValor?: number  // Valor da evolução
  evolucaoTipo?: 'percentual' | 'nominal'  // % ou R$
}

interface PatrimonioAtual {
  valor: number
  mes: string  // "2025-12" formato
  mesFormatado: string  // "Dezembro/2025"
}

export function SimuladorCenarios() {
  // Patrimônio atual (buscar da API)
  const [patrimonioAtual, setPatrimonioAtual] = useState<PatrimonioAtual | null>(null)
  const [loadingPatrimonio, setLoadingPatrimonio] = useState(true)

  // Parâmetros da simulação
  const [parametros, setParametros] = useState<ParametrosSimulacao>({
    taxaRendimentoAnual: 10.0,  // 10% ao ano
    aporteMensal: 1000.0,        // R$ 1.000/mês
    periodoMeses: 12,            // 12 meses
  })

  // Aportes Extraordinários
  const [aportesExtras, setAportesExtras] = useState<AporteExtraordinario[]>([])

  // Nome e descrição para salvar cenário
  const [nomeCenario, setNomeCenario] = useState('')
  const [descricaoCenario, setDescricaoCenario] = useState('')

  // Estado da simulação
  const [simulacao, setSimulacao] = useState<SimulacaoCenario | null>(null)
  const [loading, setLoading] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sucesso, setSucesso] = useState<string | null>(null)
  
  // DEBUG: Estado para mostrar logs na tela
  const [debugInfo, setDebugInfo] = useState<any>(null)

  // Buscar patrimônio atual ao carregar
  React.useEffect(() => {
    const buscarPatrimonioAtual = async () => {
      try {
        setLoadingPatrimonio(true)
        // ✅ FASE 1 - Autenticação automática
        const data = await apiGet<any>('/api/investimentos/historico/ultimo')
        if (data) {
          if (data && data.valor_total) {
            // anomes vem como número (202512), converter para ano e mês
            const anomesStr = String(data.anomes)
            const ano = anomesStr.substring(0, 4)
            const mes = anomesStr.substring(4, 6)
            const mesesNomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                                'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
            setPatrimonioAtual({
              valor: data.valor_total,
              mes: data.anomes,
              mesFormatado: `${mesesNomes[parseInt(mes) - 1]}/${ano}`
            })
          }
        }
      } catch (err) {
        console.error('Erro ao buscar patrimônio atual:', err)
      } finally {
        setLoadingPatrimonio(false)
      }
    }
    buscarPatrimonioAtual()
  }, [])

  // Expandir aportes recorrentes
  const expandirAportesRecorrentes = useCallback(() => {
    const aportesExpandidos: { mes: number; valor: number; descricao: string }[] = []
    
    aportesExtras.forEach(aporte => {
      if (aporte.recorrencia === 'unico') {
        // Aporte único no mês especificado
        aportesExpandidos.push({
          mes: aporte.mesAno,
          valor: aporte.valor,
          descricao: aporte.descricao
        })
      } else {
        // Aportes recorrentes
        let intervalo = 12  // anual por padrão
        if (aporte.recorrencia === 'semestral') intervalo = 6
        if (aporte.recorrencia === 'trimestral') intervalo = 3
        
        let ocorrencia = 0  // Conta quantas vezes o aporte ocorreu
        for (let mes = aporte.mesAno; mes <= parametros.periodoMeses; mes += intervalo) {
          let valorAjustado = aporte.valor
          
          // Aplicar evolução da 2ª ocorrência em diante
          if (aporte.evoluir && aporte.evolucaoValor && ocorrencia > 0) {
            if (aporte.evolucaoTipo === 'percentual') {
              // Evolução percentual composta
              valorAjustado = aporte.valor * Math.pow(1 + aporte.evolucaoValor / 100, ocorrencia)
            } else {
              // Evolução nominal linear
              valorAjustado = aporte.valor + (aporte.evolucaoValor * ocorrencia)
            }
          }
          
          aportesExpandidos.push({
            mes: mes,
            valor: valorAjustado,
            descricao: `${aporte.descricao} (${aporte.recorrencia}${ocorrencia > 0 && aporte.evoluir ? ` +${ocorrencia}` : ''})`
          })
          
          ocorrencia++
        }
      }
    })
    
    return aportesExpandidos
  }, [aportesExtras, parametros.periodoMeses])

  // Handler para executar simulação (sem salvar)
  const executarSimulacao = useCallback(async () => {
    setLoading(true)
    setError(null)
    setSucesso(null)

    try {
      // Expandir aportes extraordinários primeiro
      const aportesExpandidos = expandirAportesRecorrentes()
      
      // Criar mapa de aportes por mês para acesso rápido
      const aportesPorMes = new Map<number, number>()
      aportesExpandidos.forEach(aporte => {
        const atual = aportesPorMes.get(aporte.mes) || 0
        aportesPorMes.set(aporte.mes, atual + aporte.valor)
      })
      
      // RECALCULAR completamente com aportes extraordinários incluídos
      // IMPORTANTE: O mês 1 da simulação é o mês SEGUINTE ao patrimônio atual
      const patrimonioInicial = Number(patrimonioAtual?.valor || 0)
      const taxaMensal = Math.pow(1 + parametros.taxaRendimentoAnual / 100, 1/12) - 1
      
      // Calcular mês/ano de início (mês seguinte ao patrimônio atual)
      const anomesAtual = patrimonioAtual?.mes || 202512
      const anomesNum = Number(anomesAtual)
      const anoAtual = Math.floor(anomesNum / 100)
      const mesAtual = anomesNum % 100
      
      let patrimonioAtualCalculo = patrimonioInicial
      const projecao_mensal = []
      let totalAportes = 0
      
      // Para cálculo de patrimônio médio ponderado
      let somaPonderada = patrimonioInicial * parametros.periodoMeses  // Inicial trabalha todos os meses
      
      for (let mes = 1; mes <= parametros.periodoMeses; mes++) {
        // Calcular mês/ano real desta projeção
        const mesesDesdeInicio = mesAtual + mes  // mês seguinte ao atual
        const anoProjecao = anoAtual + Math.floor((mesesDesdeInicio - 1) / 12)
        const mesProjecao = ((mesesDesdeInicio - 1) % 12) + 1
        
        // Aplicar rendimento sobre patrimônio atual
        patrimonioAtualCalculo = patrimonioAtualCalculo * (1 + taxaMensal)
        
        // Adicionar aporte mensal regular
        const aporteMensal = Number(parametros.aporteMensal)
        patrimonioAtualCalculo += aporteMensal
        totalAportes += aporteMensal
        
        // Ponderar: quanto tempo este aporte vai trabalhar?
        const mesesRestantes = parametros.periodoMeses - mes + 1
        somaPonderada += aporteMensal * mesesRestantes
        
        // Adicionar aporte extraordinário se houver neste mês
        const aporteExtra = aportesPorMes.get(mes) || 0
        if (aporteExtra > 0) {
          patrimonioAtualCalculo += aporteExtra
          totalAportes += aporteExtra
          // Ponderar aporte extraordinário também
          somaPonderada += aporteExtra * mesesRestantes
        }
        
        projecao_mensal.push({
          mes: mes,
          mes_real: mesProjecao,
          ano_real: anoProjecao,
          patrimonio: patrimonioAtualCalculo,
          aportes_acumulados: totalAportes
        })
      }
      
      const patrimonioFinal = patrimonioAtualCalculo
      // IMPORTANTE: Patrimônio inicial conta como aporte, não como rendimento
      const totalAportesComInicial = totalAportes + patrimonioInicial
      // Rendimentos = Patrimônio Final - Todos os Aportes (incluindo inicial)
      const totalRendimentos = patrimonioFinal - totalAportesComInicial
      
      // Calcular Patrimônio Médio Ponderado (considera tempo que cada aporte trabalhou)
      const patrimonioMedioPonderado = somaPonderada / parametros.periodoMeses
      
      const totalAportesExtras = Array.from(aportesPorMes.values()).reduce((a, b) => a + b, 0)
      
      const resultado = {
        patrimonio_inicial: patrimonioInicial,
        patrimonio_final: patrimonioFinal,
        total_aportes: totalAportesComInicial,  // Inclui patrimônio inicial
        total_rendimentos: totalRendimentos,
        patrimonio_medio_ponderado: patrimonioMedioPonderado,  // NOVO: para cálculo de rentabilidade
        evolucao_mensal: [], // Placeholder para compatibilidade
        projecao_mensal: projecao_mensal
      }
      
      // Adicionar projecao_mensal se não existir (compatibilidade)
      const resultadoCompleto = {
        ...resultado,
        projecao_mensal: resultado.projecao_mensal || []
      }
      setSimulacao(resultadoCompleto)
      setSucesso('Simulação executada com sucesso!')
    } catch (err) {
      console.error('Erro ao simular cenário:', err)
      setError(err instanceof Error ? err.message : 'Erro ao simular cenário')
    } finally {
      setLoading(false)
    }
  }, [parametros, patrimonioAtual, aportesExtras, expandirAportesRecorrentes])

  // Handlers para aportes extraordinários
  const adicionarAporteExtra = () => {
    setAportesExtras([...aportesExtras, {
      id: `aporte-${Date.now()}`,
      mesAno: 12,  // Dezembro
      valor: 30000,
      descricao: '13º Salário',
      recorrencia: 'anual',
      evoluir: false,
      evolucaoValor: 0,
      evolucaoTipo: 'percentual'
    }])
  }

  const removerAporteExtra = (id: string) => {
    setAportesExtras(aportesExtras.filter(a => a.id !== id))
  }

  const atualizarAporteExtra = (id: string, campo: keyof AporteExtraordinario, valor: any) => {
    setAportesExtras(aportesExtras.map(a => 
      a.id === id ? { ...a, [campo]: valor } : a
    ))
  }

  // Meses do ano para dropdown
  const mesesDoAno = [
    { valor: 1, label: 'Janeiro' },
    { valor: 2, label: 'Fevereiro' },
    { valor: 3, label: 'Março' },
    { valor: 4, label: 'Abril' },
    { valor: 5, label: 'Maio' },
    { valor: 6, label: 'Junho' },
    { valor: 7, label: 'Julho' },
    { valor: 8, label: 'Agosto' },
    { valor: 9, label: 'Setembro' },
    { valor: 10, label: 'Outubro' },
    { valor: 11, label: 'Novembro' },
    { valor: 12, label: 'Dezembro' },
  ]

  // Handler para salvar cenário no banco
  const salvarCenario = useCallback(async () => {
    if (!nomeCenario.trim()) {
      setError('Informe um nome para o cenário')
      return
    }

    setSalvando(true)
    setError(null)
    setSucesso(null)

    try {
      const taxaMensal = Math.pow(1 + parametros.taxaRendimentoAnual / 100, 1/12) - 1
      
      await criarCenario({
        nome_cenario: nomeCenario,
        descricao: descricaoCenario || undefined,
        patrimonio_inicial: patrimonioAtual?.valor || 0,
        rendimento_mensal_pct: taxaMensal,
        aporte_mensal: parametros.aporteMensal,
        periodo_meses: parametros.periodoMeses,
      })

      setSucesso(`Cenário "${nomeCenario}" salvo com sucesso!`)
      setNomeCenario('')
      setDescricaoCenario('')
    } catch (err) {
      console.error('Erro ao salvar cenário:', err)
      setError(err instanceof Error ? err.message : 'Erro ao salvar cenário')
    } finally {
      setSalvando(false)
    }
  }, [nomeCenario, descricaoCenario, parametros])

  // Handler para atualizar parâmetro
  const atualizarParametro = (campo: keyof ParametrosSimulacao, valor: string) => {
    const valorNumerico = parseFloat(valor) || 0
    setParametros(prev => ({
      ...prev,
      [campo]: valorNumerico
    }))
  }

  // Formatar valores de forma inteligente (milhares, milhões)
  const formatarValorCompacto = (valor: number): string => {
    if (valor >= 1000000) {
      return `${(valor / 1000000).toFixed(1)}mi`
    } else if (valor >= 1000) {
      return `${(valor / 1000).toFixed(0)}k`
    }
    return valor.toFixed(0)
  }

  // Calcular métricas projetadas
  const calcularMetricas = () => {
    if (!simulacao) return null

    const { patrimonio_inicial = 0, patrimonio_final = 0, total_aportes = 0, total_rendimentos = 0 } = simulacao

    logger.log('📊 Valores da Simulação:', {
      patrimonio_inicial,
      patrimonio_final,
      total_aportes,
      total_rendimentos
    })

    // Rentabilidade Total = Rendimentos / Total Aportes
    const rentabilidadeTotal = total_aportes > 0 
      ? (total_rendimentos / total_aportes) * 100 
      : 0
    
    // Rentabilidade Anualizada = Taxa configurada
    // (em simulações, a taxa aplicada É a rentabilidade esperada)
    const rentabilidadeAnual = parametros.taxaRendimentoAnual
    
    logger.log('💰 Cálculo Rentabilidade:', {
      formula: `(${total_rendimentos} / ${total_aportes}) × 100`,
      rentabilidadeTotal,
      rentabilidadeAnual,
      taxaConfigurada: parametros.taxaRendimentoAnual
    })

    return {
      patrimonioInicial: patrimonio_inicial,
      patrimonioFinal: patrimonio_final,
      totalAportes: total_aportes,
      totalRendimentos: total_rendimentos,
      rentabilidadeTotal: rentabilidadeTotal,
      rentabilidadeAnual: rentabilidadeAnual,
    }
  }

  const metricas = calcularMetricas()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Calculator className="h-6 w-6" />
          Simulador de Cenários
        </h2>
        <p className="text-muted-foreground mt-1">
          Projete a evolução do seu portfólio com diferentes parâmetros
        </p>
      </div>

      {/* Formulário de Parâmetros */}
      <Card>
        <CardHeader>
          <CardTitle>Parâmetros da Simulação</CardTitle>
          <CardDescription>
            Configure os parâmetros para simular a evolução do seu portfólio
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Patrimônio Atual */}
          {loadingPatrimonio ? (
            <div className="p-4 bg-muted/50 rounded-md">
              <p className="text-sm text-muted-foreground">Carregando patrimônio atual...</p>
            </div>
          ) : patrimonioAtual ? (
            <div className="p-4 bg-blue-500/10 rounded-md border border-blue-500/20">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Patrimônio Atual</p>
                  <p className="text-2xl font-bold">
                    {patrimonioAtual.valor.toLocaleString('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    })}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Patrimônio reportado em {patrimonioAtual.mesFormatado}
                  </p>
                  <p className="text-xs text-blue-500/70 mt-0.5 flex items-center gap-1">
                    <Info className="h-3 w-3" />
                    Projeção começa no mês seguinte
                  </p>
                </div>
                <TrendingUp className="h-8 w-8 text-blue-500" />
              </div>
            </div>
          ) : (
            <div className="p-4 bg-muted/50 rounded-md">
              <p className="text-sm text-muted-foreground">Sem dados de patrimônio atual</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Taxa de Rendimento */}
            <div className="space-y-2">
              <Label htmlFor="taxa-rendimento" className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Taxa de Rendimento Anual (%)
              </Label>
              <Input
                id="taxa-rendimento"
                type="number"
                step="0.1"
                min="0"
                value={parametros.taxaRendimentoAnual}
                onChange={(e) => atualizarParametro('taxaRendimentoAnual', e.target.value)}
                placeholder="Ex: 10.0"
              />
              <p className="text-xs text-muted-foreground">
                Taxa anual esperada de rendimento
              </p>
            </div>

            {/* Aporte Mensal */}
            <div className="space-y-2">
              <Label htmlFor="aporte-mensal" className="flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Aporte Mensal (R$)
              </Label>
              <Input
                id="aporte-mensal"
                type="number"
                step="100"
                min="0"
                value={parametros.aporteMensal}
                onChange={(e) => atualizarParametro('aporteMensal', e.target.value)}
                placeholder="Ex: 1000"
              />
              <p className="text-xs text-muted-foreground">
                Valor mensal de novos aportes
              </p>
            </div>

            {/* Período */}
            <div className="space-y-2">
              <Label htmlFor="periodo" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Período (meses)
              </Label>
              <Input
                id="periodo"
                type="number"
                min="1"
                max="120"
                value={parametros.periodoMeses}
                onChange={(e) => atualizarParametro('periodoMeses', e.target.value)}
                placeholder="Ex: 12"
              />
              <p className="text-xs text-muted-foreground">
                Período de projeção (1-120 meses)
              </p>
            </div>
          </div>

          {/* Seção de Aportes Extraordinários */}
          <div className="border-t pt-6">
            <div className="mb-4">
              <h3 className="text-lg font-semibold flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Aportes Extraordinários
              </h3>
              <p className="text-sm text-muted-foreground">
                Adicione aportes extras em meses específicos (ex: 13º salário, bônus)
              </p>
              {patrimonioAtual && (
                <p className="text-xs text-blue-500/70 mt-2 flex items-center gap-1">
                  <Info className="h-3 w-3" />
                  Mês 1 = {(() => {
                    const anomesAtual = Number(patrimonioAtual.mes)
                    const anoAtual = Math.floor(anomesAtual / 100)
                    const mesAtual = anomesAtual % 100
                    const proximoMes = mesAtual === 12 ? 1 : mesAtual + 1
                    const proximoAno = mesAtual === 12 ? anoAtual + 1 : anoAtual
                    const mesesNomes = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
                    return `${mesesNomes[proximoMes - 1]}/${proximoAno}`
                  })()} • Mês 12 = Dezembro/{Math.floor(Number(patrimonioAtual.mes) / 100) + 1}
                </p>
              )}
            </div>

            {aportesExtras.length > 0 ? (
              <div className="space-y-3">
                {/* Tabela de Aportes */}
                <div className="rounded-md border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-3 font-medium">Mês</th>
                        <th className="text-left p-3 font-medium">Valor (R$)</th>
                        <th className="text-left p-3 font-medium">Descrição</th>
                        <th className="text-left p-3 font-medium">Recorrência</th>
                        <th className="text-left p-3 font-medium">Evolução</th>
                        <th className="text-center p-3 font-medium w-[80px]">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {aportesExtras.map((aporte) => (
                        <React.Fragment key={aporte.id}>
                          <tr className="border-t hover:bg-muted/50">
                            <td className="p-3">
                              <select
                                value={aporte.mesAno}
                                onChange={(e) => atualizarAporteExtra(aporte.id, 'mesAno', parseInt(e.target.value))}
                                className="w-full px-2 py-1 border rounded-md bg-background"
                              >
                                {mesesDoAno.map(mes => (
                                  <option key={mes.valor} value={mes.valor}>
                                    {mes.label}
                                  </option>
                                ))}
                              </select>
                            </td>
                            <td className="p-3">
                              <Input
                                type="number"
                                min="0"
                                step="1000"
                                value={aporte.valor}
                                onChange={(e) => atualizarAporteExtra(aporte.id, 'valor', parseFloat(e.target.value) || 0)}
                                className="w-32"
                                placeholder="30.000"
                              />
                            </td>
                            <td className="p-3">
                              <Input
                                type="text"
                                value={aporte.descricao}
                                onChange={(e) => atualizarAporteExtra(aporte.id, 'descricao', e.target.value)}
                                placeholder="Ex: 13º Salário"
                              />
                            </td>
                            <td className="p-3">
                              <select
                                value={aporte.recorrencia}
                                onChange={(e) => atualizarAporteExtra(aporte.id, 'recorrencia', e.target.value)}
                                className="w-full px-2 py-1 border rounded-md bg-background"
                              >
                                <option value="unico">Único</option>
                                <option value="trimestral">Trimestral</option>
                                <option value="semestral">Semestral</option>
                                <option value="anual">Anual</option>
                              </select>
                            </td>
                            <td className="p-3">
                              <div className="flex items-center gap-2">
                                <input
                                  type="checkbox"
                                  checked={aporte.evoluir}
                                  onChange={(e) => atualizarAporteExtra(aporte.id, 'evoluir', e.target.checked)}
                                  className="h-4 w-4"
                                />
                                <Label className="text-xs">Evoluir</Label>
                              </div>
                            </td>
                            <td className="p-3 text-center">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => removerAporteExtra(aporte.id)}
                              >
                                <Trash2 className="h-4 w-4 text-destructive" />
                              </Button>
                            </td>
                          </tr>
                          
                          {/* Linha expandida para configuração de evolução */}
                          {aporte.evoluir && (
                            <tr className="border-t bg-muted/30">
                              <td colSpan={6} className="p-4">
                                <div className="space-y-3">
                                  <div className="flex items-center gap-4">
                                    <Label className="text-sm font-medium">Aumentar:</Label>
                                    <Input
                                      type="number"
                                      min="0"
                                      step="0.1"
                                      value={aporte.evolucaoValor || 0}
                                      onChange={(e) => atualizarAporteExtra(aporte.id, 'evolucaoValor', parseFloat(e.target.value) || 0)}
                                      className="w-28"
                                      placeholder="5"
                                    />
                                    <div className="flex items-center gap-2">
                                      <button
                                        type="button"
                                        onClick={() => atualizarAporteExtra(aporte.id, 'evolucaoTipo', 'percentual')}
                                        className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                                          aporte.evolucaoTipo === 'percentual' 
                                            ? 'bg-primary text-primary-foreground' 
                                            : 'bg-muted hover:bg-muted/80'
                                        }`}
                                      >
                                        %
                                      </button>
                                      <button
                                        type="button"
                                        onClick={() => atualizarAporteExtra(aporte.id, 'evolucaoTipo', 'nominal')}
                                        className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                                          aporte.evolucaoTipo === 'nominal' 
                                            ? 'bg-primary text-primary-foreground' 
                                            : 'bg-muted hover:bg-muted/80'
                                        }`}
                                      >
                                        R$
                                      </button>
                                    </div>
                                    <span className="text-xs text-muted-foreground">
                                      (da 2ª ocorrência em diante)
                                    </span>
                                  </div>
                                  
                                  {/* Explicação clara para o usuário */}
                                  <div className="px-3 py-2 bg-blue-50 dark:bg-blue-950 rounded-md border border-blue-200 dark:border-blue-800">
                                    <p className="text-xs text-blue-800 dark:text-blue-200">
                                      {aporte.evolucaoTipo === 'percentual' ? (
                                        <>
                                          💡 <strong>Percentual:</strong> Digite apenas o número (ex: <strong>5</strong> = 5% ao ano).
                                          <br/>
                                          Exemplo: R$ {aporte.valor.toLocaleString('pt-BR')} → Ano 2: R$ {(aporte.valor * (1 + (aporte.evolucaoValor || 0) / 100)).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} → Ano 3: R$ {(aporte.valor * Math.pow(1 + (aporte.evolucaoValor || 0) / 100, 2)).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                                        </>
                                      ) : (
                                        <>
                                          💡 <strong>Nominal:</strong> Digite o valor em reais (ex: <strong>1000</strong> = +R$ 1.000/ano).
                                          <br/>
                                          Exemplo: R$ {aporte.valor.toLocaleString('pt-BR')} → Ano 2: R$ {(aporte.valor + (aporte.evolucaoValor || 0)).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })} → Ano 3: R$ {(aporte.valor + 2 * (aporte.evolucaoValor || 0)).toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}
                                        </>
                                      )}
                                    </p>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                {/* Botão Adicionar */}
                <Button
                  variant="outline"
                  onClick={adicionarAporteExtra}
                  className="w-full"
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Adicionar Aporte Extraordinário
                </Button>
              </div>
            ) : (
              <div className="text-center py-6 border rounded-md bg-muted/30">
                <p className="text-sm text-muted-foreground mb-4">
                  Nenhum aporte extraordinário adicionado
                </p>
                <Button
                  variant="outline"
                  onClick={adicionarAporteExtra}
                >
                  <Plus className="mr-2 h-4 w-4" />
                  Adicionar Aporte Extraordinário
                </Button>
              </div>
            )}
          </div>

          {/* Botões de Ação - Movido para o final */}
          <div className="border-t pt-6 flex flex-col sm:flex-row gap-3">
            <Button 
              onClick={executarSimulacao} 
              disabled={loading || loadingPatrimonio}
              className="flex items-center gap-2"
            >
              <Play className="h-4 w-4" />
              {loading ? 'Simulando...' : 'Executar Simulação'}
            </Button>
          </div>

          {/* Mensagens de Erro/Sucesso */}
          {error && (
            <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
              {error}
            </div>
          )}
          {sucesso && (
            <div className="p-3 rounded-md bg-green-500/10 text-green-700 dark:text-green-400 text-sm">
              {sucesso}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Resultados da Simulação */}
      {metricas && simulacao && (
        <>
          {/* Cards de Métricas */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Patrimônio Inicial</CardDescription>
                <CardTitle className="text-2xl">
                  {metricas.patrimonioInicial.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  })}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Patrimônio Final Projetado</CardDescription>
                <CardTitle className="text-2xl text-green-600">
                  {metricas.patrimonioFinal.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  })}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total de Aportes</CardDescription>
                <CardTitle className="text-2xl">
                  {metricas.totalAportes.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  })}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total de Rendimentos</CardDescription>
                <CardTitle className="text-2xl text-blue-600">
                  {metricas.totalRendimentos.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                  })}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>

          {/* Seção: Salvar Cenário no Banco de Dados */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Save className="h-5 w-5" />
                Salvar Cenário
              </CardTitle>
              <CardDescription>
                Salve este cenário no banco de dados para consultar depois
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="nome-cenario">Nome do Cenário *</Label>
                <Input
                  id="nome-cenario"
                  type="text"
                  value={nomeCenario}
                  onChange={(e) => setNomeCenario(e.target.value)}
                  placeholder="Ex: Cenário Otimista 2026"
                  maxLength={100}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="descricao-cenario">Descrição (opcional)</Label>
                <Textarea
                  id="descricao-cenario"
                  value={descricaoCenario}
                  onChange={(e) => setDescricaoCenario(e.target.value)}
                  placeholder="Descreva as premissas deste cenário..."
                  maxLength={500}
                  rows={3}
                />
              </div>

              <Button
                onClick={salvarCenario}
                disabled={salvando || !nomeCenario.trim()}
                className="w-full sm:w-auto"
              >
                <Save className="mr-2 h-4 w-4" />
                {salvando ? 'Salvando...' : 'Salvar Cenário no Banco'}
              </Button>

              <p className="text-xs text-muted-foreground">
                💾 O cenário será salvo com os parâmetros atuais e poderá ser consultado na lista de cenários salvos.
              </p>
            </CardContent>
          </Card>

          {/* Gráfico de Evolução */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Evolução do Patrimônio
              </CardTitle>
              <CardDescription>
                Projeção da evolução patrimonial ao longo de {parametros.periodoMeses} meses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {/* Gráfico de Linhas */}
                <div className="h-[400px] w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <RechartsLineChart
                      data={(() => {
                        const patrimonioInicial = patrimonioAtual?.valor || 0
                        
                        // Mês 0: Patrimônio atual (sem rendimento, apenas aporte acumulado)
                        const dados = [{
                          mes: 'Mês 0',
                          patrimonio: patrimonioInicial,
                          aportes: patrimonioInicial,  // Patrimônio inicial = aporte acumulado
                          rendimentos: 0  // Sem rendimento no mês 0
                        }]
                        
                        // Adicionar projeção dos meses seguintes
                        if (simulacao.projecao_mensal) {
                          simulacao.projecao_mensal.forEach((item) => {
                            // Aportes acumulados = patrimônio inicial + aportes do backend (converter para Number!)
                            const aportesAcumulados = Number(patrimonioInicial) + Number(item.aportes_acumulados)
                            // Rendimentos = patrimônio projetado - aportes acumulados
                            const rendimentosAcumulados = Number(item.patrimonio) - aportesAcumulados
                            
                            dados.push({
                              mes: `Mês ${item.mes}`,
                              patrimonio: Number(item.patrimonio),
                              aportes: aportesAcumulados,
                              rendimentos: rendimentosAcumulados
                            })
                          })
                        }
                        
                        return dados
                      })()}
                      margin={{ top: 50, right: 80, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                      <XAxis 
                        dataKey="mes" 
                        className="text-xs"
                        tick={{ fontSize: 12 }}
                        interval="preserveStartEnd"
                      />
                      <YAxis 
                        className="text-xs"
                        tick={{ fontSize: 12 }}
                        tickFormatter={(value) => 
                          new Intl.NumberFormat('pt-BR', {
                            notation: 'compact',
                            compactDisplay: 'short'
                          }).format(value)
                        }
                      />
                      <Tooltip 
                        formatter={(value: number) =>
                          value.toLocaleString('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          })
                        }
                        contentStyle={{ 
                          backgroundColor: 'hsl(var(--background))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '6px'
                        }}
                      />
                      <Legend 
                        wrapperStyle={{ paddingTop: '20px' }}
                        iconType="line"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="patrimonio" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        name="Patrimônio Projetado"
                        dot={false}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="aportes" 
                        stroke="#3b82f6" 
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        name="Aportes Acumulados"
                        dot={false}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="rendimentos" 
                        stroke="#a855f7" 
                        strokeWidth={2}
                        strokeDasharray="3 3"
                        name="Rendimentos Acumulados"
                        dot={false}
                      />
                      
                      {/* Linhas verticais a cada 12 meses (anos) */}
                      {(() => {
                        const linhas = []
                        const dados = simulacao.projecao_mensal || []
                        
                        for (let i = 12; i <= parametros.periodoMeses; i += 12) {
                          const dadoMes = dados.find(d => d.mes === i)
                          if (dadoMes) {
                            const patrimonioInicial = patrimonioAtual?.valor || 0
                            const patrimonioProjetado = Number(dadoMes.patrimonio)
                            const aportesAcumulados = Number(patrimonioInicial) + Number(dadoMes.aportes_acumulados)
                            const rendimentosAcumulados = patrimonioProjetado - aportesAcumulados
                            const ano = i / 12
                            
                            linhas.push(
                              <ReferenceLine
                                key={`ano-${i}`}
                                x={`Mês ${i}`}
                                stroke="#cbd5e1"
                                strokeWidth={1}
                                strokeDasharray="5 5"
                                strokeOpacity={0.4}
                                label={{
                                  value: `ANO ${ano}`,
                                  position: 'insideTopLeft',
                                  fill: '#475569',
                                  fontSize: 12,
                                  fontWeight: 700,
                                  dy: -35
                                }}
                              />
                            )
                            
                            // Adicionar labels com valores e cores
                            const valores = [
                              { valor: patrimonioProjetado, cor: '#10b981', dy: -20 },
                              { valor: aportesAcumulados, cor: '#3b82f6', dy: -8 },
                              { valor: rendimentosAcumulados, cor: '#a855f7', dy: 4 }
                            ]
                            
                            valores.forEach((item, idx) => {
                              linhas.push(
                                <ReferenceLine
                                  key={`valor-${i}-${idx}`}
                                  x={`Mês ${i}`}
                                  stroke="transparent"
                                  label={{
                                    value: formatarValorCompacto(item.valor),
                                    position: 'insideTopLeft',
                                    fill: item.cor,
                                    fontSize: 10,
                                    fontWeight: 600,
                                    dy: item.dy
                                  }}
                                />
                              )
                            })
                          }
                        }
                        return linhas
                      })()}
                    </RechartsLineChart>
                  </ResponsiveContainer>
                </div>

                {/* Resumo Final */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-muted/50 rounded-md">
                  <div>
                    <p className="text-sm text-muted-foreground">Rentabilidade Total</p>
                    <p className="text-2xl font-bold text-green-600">
                      {metricas.rentabilidadeTotal.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Rentabilidade Anualizada</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {metricas.rentabilidadeAnual.toFixed(2)}%
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
