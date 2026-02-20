'use client'

/**
 * PatrimonioTab - Gráfico de evolução Ativos (barras), Passivos (barras) e PL (linha)
 * Últimos 6 meses partindo do mês filtrado. Passivos exibidos como positivo.
 * PL no eixo secundário.
 */

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { RefreshCw, ChevronRight } from 'lucide-react'
import {
  getPatrimonioTimeline,
  getDistribuicaoPorTipo,
} from '@/features/investimentos/services/investimentos-api'
import type { PatrimonioMensal, DistribuicaoTipo } from '@/features/investimentos/types'
import { DistribuicaoLista } from './distribuicao-lista'
import { PatrimonioChart } from './patrimonio-chart'

function formatMes(anomes: number): string {
  const s = String(anomes)
  const ano = s.substring(0, 4)
  const mes = s.substring(4, 6)
  const meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  return `${meses[parseInt(mes, 10) - 1]}/${ano.substring(2)}`
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface PatrimonioTabProps {
  selectedMonth: Date
}

type DistribuicaoToggle = 'ativo' | 'passivo'

export function PatrimonioTab({ selectedMonth }: PatrimonioTabProps) {
  const router = useRouter()
  const [data, setData] = useState<PatrimonioMensal[]>([])
  const [distribuicaoAtivo, setDistribuicaoAtivo] = useState<DistribuicaoTipo[]>([])
  const [distribuicaoPassivo, setDistribuicaoPassivo] = useState<DistribuicaoTipo[]>([])
  const [distribuicaoLoading, setDistribuicaoLoading] = useState(true)
  const [distribuicaoToggle, setDistribuicaoToggle] = useState<DistribuicaoToggle>('ativo')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const anoAtual = selectedMonth.getFullYear()
  const mesAtual = selectedMonth.getMonth() + 1

  useEffect(() => {
    const anoInicio = anoAtual - 1
    const anoFim = anoAtual + 1

    getPatrimonioTimeline({ ano_inicio: anoInicio, ano_fim: anoFim })
      .then((items) => {
        setData(items)
        setError(null)
      })
      .catch((err) => {
        setError(err?.message || 'Erro ao carregar patrimônio')
        setData([])
      })
      .finally(() => setLoading(false))
  }, [anoAtual])

  const fetchDistribuicao = useCallback(() => {
    setDistribuicaoLoading(true)
    Promise.all([
      getDistribuicaoPorTipo({ classe_ativo: 'Ativo' }),
      getDistribuicaoPorTipo({ classe_ativo: 'Passivo' }),
    ])
      .then(([ativos, passivos]) => {
        setDistribuicaoAtivo(ativos)
        setDistribuicaoPassivo(passivos)
      })
      .catch(() => {
        setDistribuicaoAtivo([])
        setDistribuicaoPassivo([])
      })
      .finally(() => setDistribuicaoLoading(false))
  }, [])

  useEffect(() => {
    fetchDistribuicao()
  }, [fetchDistribuicao])

  if (loading) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-8 flex items-center justify-center min-h-[280px]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-red-600">
        <p className="text-sm">{error}</p>
      </div>
    )
  }

  if (!data || data.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-gray-500">
        <p className="text-sm">Nenhum dado de patrimônio disponível.</p>
      </div>
    )
  }

  // Últimos 6 meses partindo do mês filtrado (inclusive)
  const anomesFim = anoAtual * 100 + mesAtual
  const sorted = [...data].sort((a, b) => a.anomes - b.anomes)
  const ateFim = sorted.filter((d) => d.anomes <= anomesFim)
  const ultimos6 = ateFim.slice(-6)

  if (ultimos6.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-8 text-center text-gray-500">
        <p className="text-sm">Nenhum dado para os últimos 6 meses.</p>
      </div>
    )
  }

  const maxAtivos = Math.max(...ultimos6.map((d) => d.ativos))
  const maxPassivos = Math.max(...ultimos6.map((d) => Math.abs(d.passivos)))
  const maxBarras = Math.max(maxAtivos, maxPassivos)
  const minPl = Math.min(...ultimos6.map((d) => d.patrimonio_liquido))
  const maxPl = Math.max(...ultimos6.map((d) => d.patrimonio_liquido))
  const rangePl = maxPl - minPl || 100000

  // Barras ocupam a parte inferior; PL fica acima com gap visível
  const gap = maxBarras * 0.2 // 20% de espaço entre barras e linha
  const plZoneHeight = Math.max(rangePl, maxBarras * 0.12) // Zona PL com altura mínima
  const domainMax = maxBarras + gap + plZoneHeight * 1.15

  const chartData = ultimos6.map((d) => {
    // Normalizar PL para ocupar a zona superior (acima das barras + gap)
    const plNorm = rangePl > 0 ? (d.patrimonio_liquido - minPl) / rangePl : 0
    const plChart = maxBarras + gap + plNorm * plZoneHeight
    return {
      ...d,
      mesLabel: formatMes(d.anomes),
      ativos: d.ativos,
      passivosAbs: Math.abs(d.passivos),
      pl: d.patrimonio_liquido,
      plChart,
    }
  })

  const formatCompact = (v: number) =>
    v >= 1_000_000
      ? `${(v / 1_000_000).toFixed(1).replace('.', ',')}M`
      : v >= 1_000
        ? `${(v / 1_000).toFixed(0)}k`
        : String(v)

  // Um único eixo: barras em baixo (0 até maxBarras), linha PL em cima (maxBarras+gap até domainMax)
  const domain: [number, number] = [0, domainMax]

  const formatTooltipValue = (value: number, name: string) => {
    if (name === 'Passivos') return formatCurrency(-value)
    if (name === 'Patrimônio Líquido') {
      const plNorm = plZoneHeight > 0 ? (value - maxBarras - gap) / plZoneHeight : 0
      return formatCurrency(minPl + plNorm * rangePl)
    }
    return formatCurrency(value)
  }

  const toNum = (d: DistribuicaoTipo) =>
    Math.abs(typeof d.total_investido === 'number' ? d.total_investido : parseFloat(String(d.total_investido)) || 0)
  const totalAtivos = distribuicaoAtivo.reduce((s, d) => s + toNum(d), 0)
  const totalPassivos = distribuicaoPassivo.reduce((s, d) => s + toNum(d), 0)

  return (
    <div className="space-y-6">
      {/* Gráfico */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">
          Evolução Patrimonial (últimos 6 meses)
        </h3>
        <PatrimonioChart
          chartData={chartData}
          domain={domain}
          formatCompact={formatCompact}
          formatTooltipValue={formatTooltipValue}
        />
      </div>

      {/* Toggle Ativo / Passivo + Atualizar */}
      <div className="flex items-center justify-between gap-4 border-b border-gray-200 mb-4">
        <div className="flex gap-6">
        <button
          onClick={() => setDistribuicaoToggle('ativo')}
          className={
            distribuicaoToggle === 'ativo'
              ? 'pb-2 text-sm font-semibold text-gray-900 border-b-2 border-gray-900'
              : 'pb-2 text-sm font-semibold text-gray-400 hover:text-gray-600'
          }
        >
          Ativo
        </button>
        <button
          onClick={() => setDistribuicaoToggle('passivo')}
          className={
            distribuicaoToggle === 'passivo'
              ? 'pb-2 text-sm font-medium text-gray-900 border-b-2 border-gray-900'
              : 'pb-2 text-sm font-medium text-gray-400 hover:text-gray-600'
          }
        >
          Passivo
        </button>
        </div>
        <button
          onClick={fetchDistribuicao}
          disabled={distribuicaoLoading}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-700 disabled:opacity-50"
          title="Atualizar dados"
        >
          <RefreshCw className={`w-4 h-4 ${distribuicaoLoading ? 'animate-spin' : ''}`} />
          Atualizar
        </button>
      </div>

      {/* Lista de distribuição */}
      {distribuicaoLoading && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      )}
      {!distribuicaoLoading && distribuicaoToggle === 'ativo' && (
        <DistribuicaoLista
          distribuicao={distribuicaoAtivo}
          totalGeral={totalAtivos}
          isPassivo={false}
          onItemClick={(tipo) => {
            const anomes = anoAtual * 100 + mesAtual
            router.push(`/mobile/investimentos?tipo=${encodeURIComponent(tipo)}&anomes=${anomes}`)
          }}
        />
      )}
      {!distribuicaoLoading && distribuicaoToggle === 'passivo' && (
        <DistribuicaoLista
          distribuicao={distribuicaoPassivo}
          totalGeral={totalPassivos}
          isPassivo={true}
          onItemClick={(tipo) => {
            const anomes = anoAtual * 100 + mesAtual
            router.push(`/mobile/investimentos?tipo=${encodeURIComponent(tipo)}&anomes=${anomes}`)
          }}
        />
      )}

      {/* Link para tela de detalhamento */}
      <button
        onClick={() => router.push('/mobile/investimentos')}
        className="w-full mt-4 flex items-center justify-between py-3 px-4 rounded-xl border border-gray-200 bg-white hover:bg-gray-50 text-gray-900 font-medium"
      >
        Ver todos os investimentos
        <ChevronRight className="w-5 h-5 text-gray-400" />
      </button>
    </div>
  )
}
