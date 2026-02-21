'use client'

/**
 * Gráfico PL Realizado vs Plano - por ano
 * - Vermelho: PL realizado (último mês do ano para passado, mês com último dado para ano atual)
 * - Cinza: PL plano (ano atual = mesmo mês do realizado; demais = último mês do ano)
 * - Eixo X: ano como primeiro mês (tick "2026" = Jan 2026); x = ano + (mes-1)/12
 * - Bolas só no ano atual e último ponto da projeção
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
    const ultimoItemProj = projecao.length > 0 ? projecao[projecao.length - 1] : null
    const ultimoAnomesProj = ultimoItemProj?.anomes ?? null
    const ultimoAnoProj = ultimoAnomesProj != null ? Math.floor(ultimoAnomesProj / 100) : null

    byYear.forEach((items, ano) => {
      let patrimonio: number
      if (ano === anoAtual && anomesUltimoRealizado != null) {
        const val = projecaoByAnomes.get(anomesUltimoRealizado)
        if (val != null) {
          patrimonio = val
        } else {
          const realizadoJan = realizadoByYear.get(ano)
          if (realizadoJan != null) {
            patrimonio = realizadoJan
          } else {
            const first = [...items].sort((a, b) => a.anomes - b.anomes)[0]
            patrimonio = typeof first.patrimonio === 'number' ? first.patrimonio : parseFloat(String(first.patrimonio)) || 0
          }
        }
      } else if (ano === ultimoAnoProj && ultimoItemProj != null) {
        patrimonio = typeof ultimoItemProj.patrimonio === 'number'
          ? ultimoItemProj.patrimonio
          : parseFloat(String(ultimoItemProj.patrimonio)) || 0
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

    const mesUltimoRealizado = anomesUltimoRealizado != null && Math.floor(anomesUltimoRealizado / 100) === anoAtual
      ? anomesUltimoRealizado % 100
      : 12
    const mesUltimoPlano = ultimoAnomesProj != null && ultimoAnoProj != null && Math.floor(ultimoAnomesProj / 100) === ultimoAnoProj
      ? ultimoAnomesProj % 100
      : 12

    // Ano como primeiro mês: x = ano + (mes - 1) / 12
    // Tick "2026" = Jan 2026; Dec 2025 = 2025.917. Elimina a necessidade de posicionamento fracionário especial.
    return anosSorted.map((ano) => {
      let plPlano = planoByYearClean.get(ano) ?? null
      if (ultimoAnoProj != null && ano > ultimoAnoProj) plPlano = null

      let mes = 12
      if (ano === anoAtual) mes = mesUltimoRealizado
      else if (ano === ultimoAnoProj) mes = mesUltimoPlano
      const x = ano + (mes - 1) / 12

      return {
        year: ano,
        x,
        label: String(ano),
        plRealizado: realizadoByYear.get(ano) ?? null,
        plPlano,
      }
    })
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

  const xDomain = useMemo(() => {
    const xs = chartData.map((d) => d.x)
    if (xs.length === 0) return [0, 1]
    const min = Math.min(...xs)
    const max = Math.max(...chartData.map((d) => d.year))
    return [min, max] as [number, number]
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

  const dataWithNumbers = [...chartData]
    .sort((a, b) => a.x - b.x)
    .map((d) => ({
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

  const ultimoRealizadoIndex = dataWithNumbers.reduce(
    (last, d, i) => (d.plRealizadoNum != null ? i : last),
    -1
  )
  const ultimoPlanoIndex = dataWithNumbers.reduce(
    (last, d, i) => (d.plPlanoNum != null ? i : last),
    -1
  )

  const labelFormatter = (v: number) =>
    v >= 1_000_000 ? `${(v / 1_000_000).toFixed(1)}M` : v >= 1_000 ? `${Math.round(v / 1_000)}k` : String(v)

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 pr-6 overflow-visible">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Evolução Patrimonial</h3>
      <div className="h-56 w-full min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={dataWithNumbers}
            margin={{ top: 36, right: 16, left: 8, bottom: 8 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              type="number"
              dataKey="x"
              domain={xDomain}
              tick={{ fontSize: 10 }}
              ticks={[...anosNoEixoX].sort((a, b) => a - b)}
              tickFormatter={(v) => String(Math.round(v))}
            />
            <YAxis hide domain={[0, maxVal * 1.05]} />
            <Tooltip
              formatter={(value: number, name: string) => [
                formatCurrency(value),
                name === 'plRealizadoNum' ? 'PL Realizado' : 'PL Plano',
              ]}
              labelFormatter={(label, payload) => {
                const x = typeof label === 'number' ? label : (payload?.[0]?.payload?.x ?? Number(label))
                const year = Math.floor(x)
                const month = Math.min(12, Math.max(1, Math.round((x - year) * 12) + 1))
                const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                return `${MESES[month - 1] ?? 'Jan'} ${year}`
              }}
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
                  if (index !== ultimoRealizadoIndex) return null
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
              stroke="#4b5563"
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={(props) => {
                const { cx, cy, payload, index } = props
                if (cx == null || cy == null || !showDot(payload?.year)) return null
                return <circle key={`plano-${payload?.year ?? index}`} cx={cx} cy={cy} r={3} fill="#4b5563" />
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
                  if (index !== ultimoPlanoIndex) return null
                  return (
                    <text key={`plano-${payload?.year ?? index ?? value}`} x={x} y={y - 6} textAnchor="middle" fill="#4b5563" fontSize={10} fontWeight={700}>
                      {labelFormatter(value)}
                    </text>
                  )
                }}
              />
            </Line>
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="flex flex-wrap gap-x-6 gap-y-2 mt-3 justify-center text-xs text-gray-600 w-full">
        <span className="flex items-center gap-1.5 shrink-0">
          <span className="w-3 h-0.5 bg-red-700 rounded" />
          PL Realizado
        </span>
        <span className="flex items-center gap-1.5 shrink-0">
          <svg width="24" height="4" className="shrink-0">
            <line x1="0" y1="2" x2="24" y2="2" stroke="#4b5563" strokeWidth="2" strokeDasharray="4 3" />
          </svg>
          <span className="text-gray-600 font-medium">PL Plano</span>
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
