'use client'

/**
 * Simulador de Investimentos - Versão Mobile
 *
 * Permite simular evolução do portfólio com:
 * - Taxa de rendimento anual
 * - Aporte mensal
 * - Período de projeção
 * - Gráfico responsivo
 * - Salvar cenário
 */

import React, { useState, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Calculator, TrendingUp, Calendar, DollarSign, Play, Save } from 'lucide-react'
import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { apiGet, API_ENDPOINTS } from '@/core/config/api.config'
import { criarCenario } from '../../services/investimentos-api'
import type { ParametrosSimulacao, SimulacaoCenario } from '../../types'

interface PatrimonioAtual {
  valor: number
  mes: string
  mesFormatado: string
}

const formatCurrency = (v: number) =>
  v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

export function SimuladorMobile() {
  const [patrimonioAtual, setPatrimonioAtual] = useState<PatrimonioAtual | null>(null)
  const [loadingPatrimonio, setLoadingPatrimonio] = useState(true)

  const [parametros, setParametros] = useState<ParametrosSimulacao>({
    taxaRendimentoAnual: 10.0,
    aporteMensal: 1000.0,
    periodoMeses: 12,
  })

  const [nomeCenario, setNomeCenario] = useState('')
  const [simulacao, setSimulacao] = useState<SimulacaoCenario | null>(null)
  const [loading, setLoading] = useState(false)
  const [salvando, setSalvando] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [sucesso, setSucesso] = useState<string | null>(null)

  useEffect(() => {
    const buscarPatrimonio = async () => {
      try {
        setLoadingPatrimonio(true)
        const data = await apiGet<any>(`${API_ENDPOINTS.INVESTIMENTOS}/historico/ultimo`)
        if (data && data.valor_total != null) {
          const anomesStr = String(data.anomes || '')
          const ano = anomesStr.substring(0, 4)
          const mes = anomesStr.substring(4, 6)
          const mesesNomes = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro',
          ]
          setPatrimonioAtual({
            valor: Number(data.valor_total),
            mes: data.anomes,
            mesFormatado: `${mesesNomes[parseInt(mes, 10) - 1] || ''}/${ano}`,
          })
        }
      } catch (err) {
        // 404 ou erro: usuário sem histórico de investimentos
        console.debug('Sem patrimônio ou erro:', err)
      } finally {
        setLoadingPatrimonio(false)
      }
    }
    buscarPatrimonio()
  }, [])

  const executarSimulacao = useCallback(() => {
    setLoading(true)
    setError(null)
    setSucesso(null)

    try {
      const patrimonioInicial = Number(patrimonioAtual?.valor || 0)
      const taxaMensal = Math.pow(1 + parametros.taxaRendimentoAnual / 100, 1 / 12) - 1

      const now = new Date()
      const anomesNum = Number(patrimonioAtual?.mes || now.getFullYear() * 100 + (now.getMonth() + 1))
      const anoAtual = Math.floor(anomesNum / 100)
      const mesAtual = anomesNum % 100 || 12

      let patrimonio = patrimonioInicial
      const projecao_mensal: { mes: number; mes_label: string; patrimonio: number }[] = []
      let totalAportes = patrimonioInicial

      for (let mes = 1; mes <= parametros.periodoMeses; mes++) {
        patrimonio = patrimonio * (1 + taxaMensal) + parametros.aporteMensal
        totalAportes += parametros.aporteMensal
        const mesesDesdeInicio = mesAtual + mes
        const anoProj = anoAtual + Math.floor((mesesDesdeInicio - 1) / 12)
        const mesProj = ((mesesDesdeInicio - 1) % 12) + 1
        const mesesNomes = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez']
        projecao_mensal.push({
          mes,
          mes_label: `${mesesNomes[mesProj - 1]}/${anoProj}`,
          patrimonio: Math.round(patrimonio * 100) / 100,
        })
      }

      const totalRendimentos = patrimonio - totalAportes
      setSimulacao({
        patrimonio_inicial: patrimonioInicial,
        patrimonio_final: patrimonio,
        total_aportes: totalAportes,
        total_rendimentos: totalRendimentos,
        patrimonio_medio_ponderado: 0,
        evolucao_mensal: [],
        projecao_mensal: projecao_mensal.map((p) => ({
          mes: p.mes,
          mes_real: 0,
          ano_real: 0,
          patrimonio: p.patrimonio,
          aportes_acumulados: 0,
        })),
      })
      setSucesso('Simulação executada!')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao simular')
    } finally {
      setLoading(false)
    }
  }, [parametros, patrimonioAtual])

  const salvarCenario = useCallback(async () => {
    if (!nomeCenario.trim()) {
      setError('Informe um nome para o cenário')
      return
    }

    setSalvando(true)
    setError(null)
    setSucesso(null)

    try {
      const taxaMensal = Math.pow(1 + parametros.taxaRendimentoAnual / 100, 1 / 12) - 1
      await criarCenario({
        nome_cenario: nomeCenario.trim(),
        descricao: undefined,
        patrimonio_inicial: patrimonioAtual?.valor || 0,
        rendimento_mensal_pct: taxaMensal,
        aporte_mensal: parametros.aporteMensal,
        periodo_meses: parametros.periodoMeses,
      })
      setSucesso(`Cenário "${nomeCenario}" salvo!`)
      setNomeCenario('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSalvando(false)
    }
  }, [nomeCenario, parametros, patrimonioAtual])

  const atualizarParametro = (campo: keyof ParametrosSimulacao, valor: string) => {
    const n = parseFloat(valor) || 0
    setParametros((prev) => ({ ...prev, [campo]: n }))
  }

  const chartData = simulacao?.projecao_mensal?.map((p, i) => ({
    mes: i + 1,
    label: `${p.mes_real || i + 1}/${p.ano_real || new Date().getFullYear()}`,
    patrimonio: p.patrimonio,
  })) ?? []

  return (
    <div className="space-y-6 pb-8">
      {/* Patrimônio atual */}
      {loadingPatrimonio ? (
        <div className="p-4 bg-gray-100 rounded-xl">
          <p className="text-sm text-gray-500">Carregando patrimônio...</p>
        </div>
      ) : patrimonioAtual ? (
        <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100">
          <p className="text-sm text-gray-600">Patrimônio atual</p>
          <p className="text-xl font-bold text-gray-900">{formatCurrency(patrimonioAtual.valor)}</p>
          <p className="text-xs text-gray-500 mt-1">{patrimonioAtual.mesFormatado}</p>
        </div>
      ) : (
        <div className="p-4 bg-gray-100 rounded-xl">
          <p className="text-sm text-gray-500">Sem patrimônio cadastrado</p>
        </div>
      )}

      {/* Parâmetros */}
      <div className="space-y-4">
        <h3 className="font-semibold text-gray-900 flex items-center gap-2">
          <Calculator className="w-5 h-5" />
          Parâmetros
        </h3>

        <div className="space-y-2">
          <Label>Taxa anual (%)</Label>
          <Input
            type="number"
            step="0.1"
            min="0"
            value={parametros.taxaRendimentoAnual}
            onChange={(e) => atualizarParametro('taxaRendimentoAnual', e.target.value)}
            className="text-base"
          />
        </div>

        <div className="space-y-2">
          <Label>Aporte mensal (R$)</Label>
          <Input
            type="number"
            step="100"
            min="0"
            value={parametros.aporteMensal}
            onChange={(e) => atualizarParametro('aporteMensal', e.target.value)}
            className="text-base"
          />
        </div>

        <div className="space-y-2">
          <Label>Período (meses)</Label>
          <Input
            type="number"
            min="1"
            max="360"
            value={parametros.periodoMeses}
            onChange={(e) => atualizarParametro('periodoMeses', e.target.value)}
            className="text-base"
          />
        </div>

        <Button
          onClick={executarSimulacao}
          disabled={loading}
          className="w-full h-12 text-base font-semibold"
        >
          {loading ? (
            'Calculando...'
          ) : (
            <>
              <Play className="w-5 h-5 mr-2" />
              Simular
            </>
          )}
        </Button>
      </div>

      {/* Mensagens */}
      {error && (
        <div className="p-3 bg-red-50 text-red-700 rounded-xl text-sm">{error}</div>
      )}
      {sucesso && (
        <div className="p-3 bg-green-50 text-green-700 rounded-xl text-sm">{sucesso}</div>
      )}

      {/* Resultado e gráfico */}
      {simulacao && (
        <div className="space-y-4">
          <h3 className="font-semibold text-gray-900">Projeção</h3>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-gray-50 rounded-xl">
              <p className="text-xs text-gray-500">Patrimônio final</p>
              <p className="font-bold text-gray-900">{formatCurrency(simulacao.patrimonio_final)}</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-xl">
              <p className="text-xs text-gray-500">Rendimentos</p>
              <p className="font-bold text-emerald-600">
                +{formatCurrency(simulacao.total_rendimentos)}
              </p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis
                  dataKey="mes"
                  tick={{ fontSize: 10 }}
                  tickFormatter={(v) => `M${v}`}
                />
                <YAxis
                  tick={{ fontSize: 10 }}
                  tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : String(v))}
                />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(value), 'Patrimônio']}
                  labelFormatter={(_, payload) =>
                    payload?.[0] ? `Mês ${payload[0].payload?.mes}` : ''
                  }
                />
                <Line
                  type="monotone"
                  dataKey="patrimonio"
                  stroke="#4f46e5"
                  strokeWidth={2}
                  dot={false}
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>

          {/* Salvar cenário */}
          <div className="space-y-2">
            <Label>Salvar cenário</Label>
            <div className="flex gap-2">
              <Input
                placeholder="Nome do cenário"
                value={nomeCenario}
                onChange={(e) => setNomeCenario(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={salvarCenario}
                disabled={salvando || !nomeCenario.trim()}
                variant="secondary"
              >
                {salvando ? '...' : <Save className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
