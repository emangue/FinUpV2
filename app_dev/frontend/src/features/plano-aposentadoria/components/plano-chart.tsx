'use client'

/**
 * Gráfico PL Realizado vs Plano - por ano
 * - Vermelho: PL realizado (último mês do ano para passado, mês com último dado para ano atual)
 * - Cinza: PL plano (ano atual = mesmo mês do realizado; demais = último mês do ano)
 * - Bolas só no ano atual e último ponto da projeção
 * - Labels vermelhos em todos os pontos
 */

import { useState, useEffect, useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LabelList,
} from 'recharts'
import {
  getPatrimonioTimeline,
  getCenarioProjecao,
  getCenario,
} from '@/features/investimentos/services/investimentos-api'
import type { PatrimonioMensal, ProjecaoItem } from '@/features/investimentos/types'

function formatCurrency(value: number) {
  if (value >= 1_000_000) return `R$ ${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `R$ ${Math.round(value / 1_000)} mil`
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

interface PlanoChartProps {
  /** ID do cenário principal para projeção. Se não informado, mostra só PL realizado */
  cenarioId?: number | null
}

export function PlanoChart({ cenarioId }: PlanoChartProps) {
  const [timeline, setTimeline] = useState<PatrimonioMensal[]>([])
  const [projecao, setProjecao] = useState<ProjecaoItem[]>([])
  const [cenario, setCenario] = useState<{ patrimonio_inicial: number; aporte_mensal: number } | null>(null)
  const [showPrimeirosMeses, setShowPrimeirosMeses] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const anoAtual = new Date().getFullYear()

  useEffect(() => {
    setLoading(true)
    setError(null)
    setCenario(null)
    const anoInicio = anoAtual - 5
    const anoFim = anoAtual + 35

    Promise.all([
      getPatrimonioTimeline({ ano_inicio: anoInicio, ano_fim: anoFim }),
      cenarioId ? getCenarioProjecao(cenarioId) : Promise.resolve([]),
      cenarioId ? getCenario(cenarioId) : Promise.resolve(null),
    ])
      .then(([tl, pr, c]) => {
        setTimeline(tl || [])
        setProjecao(pr || [])
        if (c) {
          const pi = parseFloat(String(c.patrimonio_inicial)) || 0
          const am = parseFloat(String(c.aporte_mensal)) || 0
          setCenario({ patrimonio_inicial: pi, aporte_mensal: am })
        }
        if (cenarioId && (!pr || pr.length === 0) && process.env.NODE_ENV === 'development') {
          console.warn('[PlanoChart] Projeção vazia para cenário', cenarioId, '- reinicie o backend para ativar recálculo automático')
        }
      })
      .catch((err) => {
        setError(err?.message || 'Erro ao carregar dados')
        setTimeline([])
        setProjecao([])
        setCenario(null)
      })
      .finally(() => setLoading(false))
  }, [cenarioId, anoAtual])

  const chartData = useMemo(() => {
    // PL realizado por ano
    // Anos anteriores: último mês (dez) do ano
    // Ano atual: mês com último dado realizado
    const realizadoByYear = new Map<number, number>()
    const sorted = [...timeline].sort((a, b) => a.anomes - b.anomes)
    let anomesUltimoRealizado: number | null = null
    for (const d of sorted) {
      const ano = d.ano
      const pl = d.patrimonio_liquido
      if (ano < anoAtual) {
        if (d.mes === 12) realizadoByYear.set(ano, pl)
      } else if (ano === anoAtual) {
        realizadoByYear.set(ano, pl)
        anomesUltimoRealizado = d.anomes
      }
    }
    const anosComDado = [...new Set(sorted.map((d) => d.ano))].filter((a) => a <= anoAtual)
    for (const ano of anosComDado) {
      if (ano < anoAtual && !realizadoByYear.has(ano)) {
        const doAno = sorted.filter((d) => d.ano === ano)
        if (doAno.length > 0) {
          const ultimo = doAno[doAno.length - 1]
          realizadoByYear.set(ano, ultimo.patrimonio_liquido)
        }
      }
    }

    // Projeção por anomes (para alinhar ano atual ao mesmo mês do realizado)
    const projecaoByAnomes = new Map<number, number>()
    for (const p of projecao) {
      const patrimonio = typeof p.patrimonio === 'number' ? p.patrimonio : parseFloat(String(p.patrimonio)) || 0
      projecaoByAnomes.set(p.anomes, patrimonio)
    }

    // PL plano por ano: ano atual = mesmo mês do realizado; demais = último mês do ano
    const planoByYearClean = new Map<number, number>()
    const byYear = new Map<number, ProjecaoItem[]>()
    for (const p of projecao) {
      const ano = Math.floor(p.anomes / 100)
      if (!byYear.has(ano)) byYear.set(ano, [])
      byYear.get(ano)!.push(p)
    }
    byYear.forEach((items, ano) => {
      let patrimonio: number
      if (ano === anoAtual && anomesUltimoRealizado != null) {
        const val = projecaoByAnomes.get(anomesUltimoRealizado)
        if (val != null) {
          patrimonio = val
        } else {
          // Plano feito em jan: sem match exato (ex. plano começa em fev), usar valor do realizado em jan
          const realizadoJan = realizadoByYear.get(ano)
          if (realizadoJan != null) {
            patrimonio = realizadoJan
          } else {
            const first = [...items].sort((a, b) => a.anomes - b.anomes)[0]
            patrimonio = typeof first.patrimonio === 'number' ? first.patrimonio : parseFloat(String(first.patrimonio)) || 0
          }
        }
      } else {
        const last = [...items].sort((a, b) => b.anomes - a.anomes)[0]
        patrimonio = typeof last.patrimonio === 'number' ? last.patrimonio : parseFloat(String(last.patrimonio)) || 0
      }
      planoByYearClean.set(ano, patrimonio)
    })

    const anos = new Set<number>()
    realizadoByYear.forEach((_, a) => anos.add(a))
    planoByYearClean.forEach((_, a) => anos.add(a))
    const anosSorted = [...anos].sort((a, b) => a - b)

    return anosSorted.map((ano) => ({
      year: ano,
      label: String(ano),
      plRealizado: realizadoByYear.get(ano) ?? null,
      plPlano: planoByYearClean.get(ano) ?? null,
    }))
  }, [timeline, projecao, anoAtual])

  // Anos que aparecem no eixo X (ticks) - mostrar labels só nesses. SEMPRE chamar (Rules of Hooks)
  const anosNoEixoX = useMemo(() => {
    const anos = chartData.map((d) => d.year)
    if (anos.length <= 7) return new Set(anos)
    const first = anos[0]
    const last = anos[anos.length - 1]
    const step = Math.max(1, Math.floor((last - first) / 6))
    const set = new Set<number>()
    for (let y = first; y <= last; y += step) set.add(y)
    set.add(last)
    return set
  }, [chartData])

  if (loading) {
    return (
      <div className="h-56 flex items-center justify-center rounded-xl border border-gray-200 bg-gray-50">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-56 flex items-center justify-center rounded-xl border border-gray-200 bg-red-50">
        <p className="text-sm text-red-600">{error}</p>
      </div>
    )
  }

  const dataWithNumbers = chartData.map((d) => ({
    ...d,
    plRealizadoNum: d.plRealizado ?? undefined,
    plPlanoNum: d.plPlano ?? undefined,
  }))

  const maxVal = Math.max(
    ...dataWithNumbers.flatMap((d) => [d.plRealizadoNum ?? 0, d.plPlanoNum ?? 0]),
    1000
  )

  // Último ano da projeção (para mostrar bola só nele e no ano atual)
  const ultimoAnoProjecao = (() => {
    const comPlano = dataWithNumbers.filter((d) => d.plPlano != null)
    return comPlano.length > 0 ? comPlano[comPlano.length - 1].year : null
  })()

  const showDot = (year: number) =>
    year === anoAtual || year === ultimoAnoProjecao

  const labelFormatter = (v: number) =>
    v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M` : v >= 1_000 ? `${Math.round(v / 1_000)}k` : String(v)

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Evolução Patrimonial</h3>
      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={dataWithNumbers}
            margin={{ top: 20, right: 10, left: 0, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="label"
              tick={{ fontSize: 10 }}
              ticks={[...anosNoEixoX].sort((a, b) => a - b).map(String)}
            />
            <YAxis
              tick={{ fontSize: 10 }}
              tickFormatter={(v) => (v >= 1e6 ? `${(v / 1e6).toFixed(1)}M` : v >= 1e3 ? `${(v / 1e3).toFixed(0)}k` : String(v))}
              domain={[0, maxVal * 1.05]}
            />
            <Tooltip
              formatter={(value: number, name: string) => [
                formatCurrency(value),
                name === 'plRealizadoNum' ? 'PL Realizado' : 'PL Plano',
              ]}
              labelFormatter={(label) => `Ano ${label}`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '12px',
              }}
            />
            <Line
              type="monotone"
              dataKey="plRealizadoNum"
              stroke="#b91c1c"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload, index } = props
                if (cx == null || cy == null || !showDot(payload?.year)) return null
                return <circle key={`realizado-${payload?.year ?? index}`} cx={cx} cy={cy} r={3} fill="#b91c1c" />
              }}
              connectNulls={false}
              name="PL Realizado"
            >
              <LabelList
                dataKey="plRealizadoNum"
                position="top"
                content={(props: { x?: number; y?: number; value?: number; index?: number; payload?: { year?: number } }) => {
                  const { x, y, value, index, payload } = props
                  if (value == null || x == null || y == null) return null
                  return (
                    <text key={payload?.year ?? index ?? value} x={x} y={y - 6} textAnchor="middle" fill="#b91c1c" fontSize={10} fontWeight={700}>
                      {labelFormatter(value)}
                    </text>
                  )
                }}
              />
            </Line>
            <Line
              type="monotone"
              dataKey="plPlanoNum"
              stroke="#9ca3af"
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={(props) => {
                const { cx, cy, payload, index } = props
                if (cx == null || cy == null || !showDot(payload?.year)) return null
                return <circle key={`plano-${payload?.year ?? index}`} cx={cx} cy={cy} r={3} fill="#9ca3af" />
              }}
              connectNulls={false}
              name="PL Plano"
            >
              <LabelList
                dataKey="plPlanoNum"
                position="top"
                content={(props: { x?: number; y?: number; value?: number; index?: number; payload?: { year?: number } }) => {
                  const { x, y, value, index, payload } = props
                  if (value == null || x == null || y == null) return null
                  return (
                    <text key={`plano-${payload?.year ?? index ?? value}`} x={x} y={y - 6} textAnchor="middle" fill="#9ca3af" fontSize={10} fontWeight={700}>
                      {labelFormatter(value)}
                    </text>
                  )
                }}
              />
            </Line>
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="flex gap-4 mt-2 justify-center text-xs text-gray-600">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-0.5 bg-red-700 rounded" />
          PL Realizado
        </span>
        <span className="flex items-center gap-1.5">
          <svg width="24" height="4" className="text-gray-400">
            <line x1="0" y1="2" x2="24" y2="2" stroke="currentColor" strokeWidth="2" strokeDasharray="4 3" />
          </svg>
          PL Plano
        </span>
      </div>

      {/* Primeiros meses do plano - patrimônio inicial + aportes */}
      {cenarioId && projecao.length > 0 && (
        <div className="mt-4 border-t border-gray-200 pt-3">
          <button
            type="button"
            onClick={() => setShowPrimeirosMeses((s) => !s)}
            className="text-xs font-medium text-gray-600 hover:text-gray-900 flex items-center gap-1"
          >
            {showPrimeirosMeses ? '▼' : '▶'} Primeiros meses do plano (patrimônio inicial + aportes)
          </button>
          {showPrimeirosMeses && (
            <div className="mt-2 overflow-x-auto">
              {(() => {
                const sorted = [...timeline].sort((a, b) => a.anomes - b.anomes)
                const ultimoRealizado = sorted.filter((d) => d.ano === anoAtual).pop()
                const anomesRealizado = ultimoRealizado ? ultimoRealizado.anomes : null
                const anoR = anomesRealizado ? Math.floor(anomesRealizado / 100) : null
                const mesR = anomesRealizado ? anomesRealizado % 100 : null
                return (
                  <>
                    {anomesRealizado != null && (
                      <p className="text-xs text-gray-500 mb-2">
                        Realizado ano atual: último dado = {anoR}-{String(mesR).padStart(2, '0')} (anomes {anomesRealizado})
                      </p>
                    )}
                    <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-1 px-2 font-semibold text-gray-700">Período</th>
                    <th className="text-left py-1 px-2 font-semibold text-gray-700">Ano/Mês</th>
                    <th className="text-right py-1 px-2 font-semibold text-gray-700">Aporte</th>
                    <th className="text-right py-1 px-2 font-semibold text-gray-700">Patrimônio fim</th>
                  </tr>
                </thead>
                <tbody>
                  {cenario && (
                    <tr className="border-b border-gray-100 bg-gray-50">
                      <td className="py-1 px-2 text-gray-500">Início</td>
                      <td className="py-1 px-2 text-gray-500">—</td>
                      <td className="py-1 px-2 text-right text-gray-500">—</td>
                      <td className="py-1 px-2 text-right font-medium text-gray-900">
                        {formatCurrency(cenario.patrimonio_inicial)}
                      </td>
                    </tr>
                  )}
                  {projecao.slice(0, 24).map((p, i) => {
                    const ano = Math.floor(p.anomes / 100)
                    const mes = p.anomes % 100
                    const MESES_ABREV = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    const mesNome = MESES_ABREV[mes - 1] ?? String(mes)
                    const aporte = typeof p.aporte === 'number' ? p.aporte : parseFloat(String(p.aporte)) || 0
                    const patrimonio = typeof p.patrimonio === 'number' ? p.patrimonio : parseFloat(String(p.patrimonio)) || 0
                    return (
                      <tr key={`${p.anomes}-${i}`} className="border-b border-gray-100">
                        <td className="py-1 px-2 text-gray-600">{mesNome} {ano}</td>
                        <td className="py-1 px-2 text-gray-600">{ano}-{String(mes).padStart(2, '0')}</td>
                        <td className="py-1 px-2 text-right text-gray-600">{formatCurrency(aporte)}</td>
                        <td className="py-1 px-2 text-right font-medium text-gray-900">{formatCurrency(patrimonio)}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
                  </>
                )
              })()}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
