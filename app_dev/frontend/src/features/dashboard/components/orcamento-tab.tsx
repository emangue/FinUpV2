'use client'

/**
 * OrcamentoTab - Tab Orçamento completo
 * Usa os MESMOS dados da tela Metas: GET /budget/planning (budget_planning + valor_realizado)
 * Layout: Resumo do Mês, Rendimentos, Despesas vs Plano, Investimentos vs Plano
 * Sprint E: Investimentos vs Plano = aporte do cenário (única fonte); sem cenário = CTA
 * Sprint G: Despesas, Receitas e Cartões como collapses (total vs plano visível no header de Despesas)
 */

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ChevronDown } from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { fetchIncomeSources, fetchCreditCards, fetchAportePrincipalPorMes, fetchAportePrincipalPeriodo, fetchOrcamentoInvestimentos } from '../services/dashboard-api'
import type { IncomeSource } from '../types'
import { fetchGoals } from '@/features/goals/services/goals-api'
import type { Goal } from '@/features/goals/types'
import { getGoalColor } from '@/features/goals/lib/colors'

const EMOJI_MAP: Record<string, string> = {
  Salário: '💼',
  Dividendos: '📈',
  Aluguel: '🏠',
  Freelance: '✏️',
  Investimentos: '📊',
  Outros: '📎',
}

function getEmoji(grupo: string): string {
  return EMOJI_MAP[grupo] ?? '📌'
}

interface OrcamentoTabProps {
  year: number
  month?: number
  /** Sprint G: layout para tab Resultado */
  variant?: 'full' | 'resultado'
  /** Sprint G: inserir entre Resumo e o restante (ex: gráfico) */
  insertBetweenResumoAndRest?: React.ReactNode
  /** Sprint G: componente GastosPorCartaoBox para collapse Cartões */
  gastosPorCartao?: React.ReactNode
  /** Métricas do período (usadas no Resumo quando month undefined = ano/YTD) */
  metrics?: { total_receitas: number; total_despesas: number } | null
  /** YTD: mês limite (1-12). Quando month undefined e ytdMonth informado, usa Jan..ytdMonth para investimentos */
  ytdMonth?: number
}

export function OrcamentoTab({
  year,
  month,
  variant = 'full',
  insertBetweenResumoAndRest,
  gastosPorCartao,
  metrics: metricsProp,
  ytdMonth: ytdMonthProp,
}: OrcamentoTabProps) {
  const router = useRouter()
  const [receitas, setReceitas] = useState<{ sources: IncomeSource[]; total_receitas: number } | null>(null)
  const [goals, setGoals] = useState<Goal[]>([])
  const [cardsTotal, setCardsTotal] = useState<number | null>(null)
  const [aportePrincipal, setAportePrincipal] = useState<number>(0)
  const [totalInvestidoPeriodo, setTotalInvestidoPeriodo] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const selectedMonth = new Date(year, (month ?? 1) - 1, 1)
        const mesRef = month ?? 1
        const isAnoOuYtd = month == null
        const results = await Promise.allSettled([
          fetchIncomeSources(year, month ?? undefined),
          fetchGoals(selectedMonth),
          fetchCreditCards(year, month ?? undefined),
          isAnoOuYtd
            ? fetchAportePrincipalPeriodo(year, ytdMonthProp)
            : fetchAportePrincipalPorMes(year, mesRef),
          isAnoOuYtd ? fetchOrcamentoInvestimentos(year, undefined, ytdMonthProp) : Promise.resolve(null),
        ])
        const inc = results[0].status === 'fulfilled' ? results[0].value : null
        const budgets = results[1].status === 'fulfilled' ? results[1].value : null
        const cards = results[2].status === 'fulfilled' ? results[2].value : null
        const aporte = results[3].status === 'fulfilled' ? results[3].value : null
        const orcInv = results[4].status === 'fulfilled' ? results[4].value : null
        setReceitas(inc && typeof inc === 'object' && 'sources' in inc ? inc : null)
        setGoals(Array.isArray(budgets) ? budgets : [])
        setCardsTotal(Array.isArray(cards) ? cards.reduce((s: number, c: { total: number }) => s + c.total, 0) : null)
        setAportePrincipal(typeof aporte === 'number' ? aporte : 0)
        setTotalInvestidoPeriodo(orcInv && typeof orcInv === 'object' && 'total_investido' in orcInv ? orcInv.total_investido : null)
      } catch {
        setReceitas(null)
        setGoals([])
        setCardsTotal(null)
        setAportePrincipal(0)
        setTotalInvestidoPeriodo(null)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [year, month, ytdMonthProp])

  // Mesmos dados da tela Metas: separar por categoria_geral
  const goalsDespesasRaw = goals.filter((g) => g.categoria_geral !== 'Investimentos')
  // Ordenar: realizado desc, depois planejado desc como desempate
  const goalsDespesas = [...goalsDespesasRaw].sort((a, b) => {
    const diffR = (b.valor_realizado ?? 0) - (a.valor_realizado ?? 0)
    if (diffR !== 0) return diffR
    return (b.valor_planejado ?? 0) - (a.valor_planejado ?? 0)
  })
  const goalsInvestimentos = goals.filter((g) => g.categoria_geral === 'Investimentos')

  // Navegar para tela de transações filtrada por grupo + período
  const navegarParaTransacoes = (grupo: string, subgrupo?: string) => {
    const params = new URLSearchParams({ grupo, from: 'orcamento' })
    if (month != null) {
      params.set('year', String(year))
      params.set('month', String(month))
    } else {
      params.set('year', String(year))
    }
    if (subgrupo) params.set('subgrupo', subgrupo)
    router.push(`/mobile/transactions?${params.toString()}`)
  }

  // Quando month undefined (ano/YTD), usar metrics para totais (goals = só 1 mês)
  const useMetricsForResumo = month == null && metricsProp
  const totalDespesas = useMetricsForResumo
    ? (metricsProp?.total_despesas ?? 0)
    : goalsDespesas.reduce((s, g) => s + (g.valor_realizado ?? 0), 0)
  const totalPlanejadoDesp = goalsDespesas.reduce((s, g) => s + (g.valor_planejado ?? 0), 0)
  const totalInvestido = useMetricsForResumo && totalInvestidoPeriodo != null
    ? totalInvestidoPeriodo
    : goalsInvestimentos.reduce((s, g) => s + (g.valor_realizado ?? 0), 0)
  // Aporte planejado vem do cenário principal (plano de aposentadoria na aba Patrimônio)
  const totalPlanejadoInv = aportePrincipal
  const percentualDesp = totalPlanejadoDesp > 0 ? (totalDespesas / totalPlanejadoDesp) * 100 : 0

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(v)

  if (loading) {
    return (
      <div className="py-10 flex justify-center">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-900" />
      </div>
    )
  }

  const totalReceitas = useMetricsForResumo
    ? (metricsProp?.total_receitas ?? 0)
    : (receitas?.total_receitas ?? 0)
  const dentroDoPlanoDesp = totalPlanejadoDesp > 0 && percentualDesp <= 100
  const diffDesp = totalPlanejadoDesp - totalDespesas
  const investidoOk = totalPlanejadoInv > 0 && totalInvestido >= totalPlanejadoInv
  const pctInvestidoVsPlano = totalPlanejadoInv > 0 ? (totalInvestido / totalPlanejadoInv) * 100 : 0
  const vezesAcimaPlano = totalPlanejadoInv > 0 ? totalInvestido / totalPlanejadoInv : 0

  // Quando totalPlanejadoDesp é 0: mostrar "Dentro do plano" só se despesas também forem 0
  const badgeDentro = totalPlanejadoDesp > 0 ? dentroDoPlanoDesp : totalDespesas <= 0

  // Label investimentos: % correto ou "X vezes o plano"
  const labelInvestidos = totalPlanejadoInv > 0
    ? investidoOk
      ? vezesAcimaPlano > 1
        ? vezesAcimaPlano >= 2
          ? `${vezesAcimaPlano.toFixed(1).replace('.', ',')}x o plano`
          : `${Math.round(pctInvestidoVsPlano)}% do plano`
        : '100% do aporte'
      : `${Math.round(pctInvestidoVsPlano)}% do aporte`
    : 'sem plano'

  const isResultadoVariant = variant === 'resultado'

  return (
    <div className="space-y-4">
      {/* Resumo do Mês */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-gray-900">Resumo do Mês</h3>
          <span
            className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
              badgeDentro ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'
            }`}
          >
            {badgeDentro ? 'Dentro do plano' : 'Acima do plano'}
          </span>
        </div>
        <div className="grid grid-cols-3 gap-3 text-center">
          <div className="py-2">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-0.5">Receitas</p>
            <p className="text-sm font-bold text-emerald-600">{formatCurrency(totalReceitas)}</p>
            <p className="text-[9px] text-gray-400 mt-0.5">sem plano</p>
          </div>
          <div className="py-2 border-x border-gray-100">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-0.5">Despesas</p>
            <p className="text-sm font-bold text-red-500">{formatCurrency(totalDespesas)}</p>
            <p className="text-[9px] font-medium mt-0.5">
              {totalPlanejadoDesp > 0 ? (
                diffDesp >= 0 ? (
                  <span className="text-emerald-500">{formatCurrency(diffDesp)} abaixo</span>
                ) : (
                  <span className="text-red-500">{formatCurrency(-diffDesp)} acima</span>
                )
              ) : (
                <span className="text-gray-400">sem plano</span>
              )}
            </p>
          </div>
          <div className="py-2">
            <p className="text-[10px] text-gray-400 uppercase tracking-wide mb-0.5">Investidos</p>
            <p className="text-sm font-bold text-blue-600">{formatCurrency(totalInvestido)}</p>
            <p className="text-[9px] font-medium mt-0.5">
              {totalPlanejadoInv > 0 ? (
                investidoOk ? (
                  <span className="text-emerald-500">{labelInvestidos}</span>
                ) : (
                  <span className="text-amber-500">{labelInvestidos}</span>
                )
              ) : (
                <span className="text-gray-400">{labelInvestidos}</span>
              )}
            </p>
          </div>
        </div>
      </div>

      {/* Sprint G: Gráfico entre Resumo e o restante */}
      {insertBetweenResumoAndRest}

      {/* Sprint G: 3 collapses - Despesas, Receitas, Cartões */}
      {isResultadoVariant ? (
        <>
          {/* Collapse Despesas - barra fora do collapse; total vs plano sempre visível */}
          <Collapsible defaultOpen={false} className="group rounded-xl border border-gray-200 bg-white overflow-hidden">
            <CollapsibleTrigger className="w-full p-4 hover:bg-gray-50 transition-colors text-left">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h3 className="text-sm font-bold text-gray-900">Despesas vs Plano</h3>
                  <p className="text-[10px] text-gray-400 mt-0.5">
                    Orçado: {formatCurrency(totalPlanejadoDesp)} ·{' '}
                    {totalPlanejadoDesp > 0
                      ? diffDesp >= 0
                        ? `Restam ${formatCurrency(diffDesp)}`
                        : `Acima ${formatCurrency(-diffDesp)}`
                      : 'Sem plano definido'}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="text-sm font-bold text-red-500">{formatCurrency(totalDespesas)}</span>
                  <ChevronDown className="w-5 h-5 text-gray-400 group-data-[state=open]:rotate-180 transition-transform" />
                </div>
              </div>
              {/* Barra fora do collapse - sempre visível */}
              <div className="mt-2">
                <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden relative">
                  <div
                    className="h-full rounded-full bg-gray-900 transition-all"
                    style={{ width: `${Math.min(percentualDesp, 100)}%` }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-[9px] text-gray-400">R$ 0</span>
                  <span className="text-[9px] text-gray-400">{formatCurrency(totalPlanejadoDesp)}</span>
                </div>
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="px-4 pb-4">
              <div className="space-y-3.5">
                {goalsDespesas
                  .filter((g) => (g.valor_realizado ?? 0) > 0 || (g.valor_planejado ?? 0) > 0)
                  .map((cat, idx) => {
                    const realizado = cat.valor_realizado ?? 0
                    const planejado = cat.valor_planejado ?? 0
                    const diff = realizado - planejado
                    const pct = planejado > 0 ? (realizado / planejado) * 100 : 0
                    const isOver = realizado > planejado
                    const color = getGoalColor(cat.grupo, idx)
                    const highlightText =
                      diff >= 0 ? `+${formatCurrency(diff)}` : `-${formatCurrency(-diff)}`
                    const highlightClass =
                      diff > 0
                        ? 'text-red-500 font-semibold'
                        : diff < 0
                          ? 'text-emerald-600 font-semibold'
                          : 'text-gray-500 font-medium'
                    return (
                      <div
                        key={cat.grupo}
                        role="button"
                        tabIndex={0}
                        onClick={() => navegarParaTransacoes(cat.grupo)}
                        onKeyDown={(e) => e.key === 'Enter' && navegarParaTransacoes(cat.grupo)}
                        className="cursor-pointer rounded-xl hover:bg-gray-50 active:bg-gray-100 transition-colors -mx-2 px-2 py-1"
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-2 shrink-0 min-w-0">
                            <div
                              className="w-2.5 h-2.5 rounded-full shrink-0"
                              style={{ backgroundColor: color }}
                            />
                            <span className="text-sm text-gray-800 truncate">{cat.grupo}</span>
                          </div>
                          <div className="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
                            <span className={`text-xs ${highlightClass}`}>{highlightText}</span>
                            <span className="text-sm font-semibold text-gray-900">
                              {formatCurrency(realizado)}
                            </span>
                            <span className="text-[9px] text-gray-400">/ {formatCurrency(planejado)}</span>
                            <ChevronDown className="w-3.5 h-3.5 text-gray-400 -rotate-90 ml-0.5" />
                          </div>
                        </div>
                        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${Math.min(pct, 100)}%`,
                              backgroundColor: isOver ? '#f87171' : color,
                            }}
                          />
                        </div>
                      </div>
                    )
                  })}
              </div>
            </CollapsibleContent>
          </Collapsible>

          {/* Collapse Receitas */}
          <Collapsible defaultOpen={false} className="group rounded-xl border border-gray-200 bg-white overflow-hidden mt-4">
            <CollapsibleTrigger className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left">
              <h3 className="text-sm font-bold text-gray-900">Rendimentos</h3>
              <div className="flex items-center gap-2 shrink-0">
                <span className="text-sm font-bold text-emerald-600">{formatCurrency(totalReceitas)}</span>
                <ChevronDown className="w-5 h-5 text-gray-400 group-data-[state=open]:rotate-180 transition-transform" />
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="px-4 pb-4">
              <div className="space-y-3">
                {(receitas?.sources ?? []).map((item) => (
                  <div key={item.fonte} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                        <span className="text-sm">{getEmoji(item.fonte)}</span>
                      </div>
                      <p className="text-sm text-gray-900 font-medium">{item.fonte}</p>
                    </div>
                    <p className="text-sm font-semibold text-gray-900">{formatCurrency(item.total)}</p>
                  </div>
                ))}
                {(!receitas?.sources || receitas.sources.length === 0) && (
                  <p className="text-xs text-gray-400 py-2">Sem receitas no período</p>
                )}
              </div>
            </CollapsibleContent>
          </Collapsible>

          {/* Collapse Cartões */}
          <Collapsible defaultOpen={false} className="group rounded-xl border border-gray-200 bg-white overflow-hidden mt-4">
            <CollapsibleTrigger className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors text-left">
              <h3 className="text-sm font-bold text-gray-900">Gastos por Cartão</h3>
              <div className="flex items-center gap-2 shrink-0">
                {cardsTotal != null && (
                  <span className="text-sm font-bold text-gray-900">{formatCurrency(cardsTotal)}</span>
                )}
                <ChevronDown className="w-5 h-5 text-gray-400 group-data-[state=open]:rotate-180 transition-transform" />
              </div>
            </CollapsibleTrigger>
            <CollapsibleContent className="px-0 pb-0">
              {gastosPorCartao}
            </CollapsibleContent>
          </Collapsible>
        </>
      ) : (
        <>
          {/* Variant full: layout original sem collapses */}
          <div className="rounded-xl border border-gray-200 bg-white p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-bold text-gray-900">Rendimentos</h3>
              <span className="text-sm font-bold text-emerald-600">{formatCurrency(totalReceitas)}</span>
            </div>
            <div className="space-y-3">
              {(receitas?.sources ?? []).map((item) => (
                <div key={item.fonte} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-emerald-100 flex items-center justify-center">
                      <span className="text-sm">{getEmoji(item.fonte)}</span>
                    </div>
                    <p className="text-sm text-gray-900 font-medium">{item.fonte}</p>
                  </div>
                  <p className="text-sm font-semibold text-gray-900">{formatCurrency(item.total)}</p>
                </div>
              ))}
              {(!receitas?.sources || receitas.sources.length === 0) && (
                <p className="text-xs text-gray-400 py-2">Sem receitas no período</p>
              )}
            </div>
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-4">
            <div className="flex items-center justify-between mb-1">
              <h3 className="text-sm font-bold text-gray-900">Despesas vs Plano</h3>
              <span className="text-sm font-bold text-red-500">{formatCurrency(totalDespesas)}</span>
            </div>
            <p className="text-[10px] text-gray-400 mb-4">
              Orçado: {formatCurrency(totalPlanejadoDesp)} ·{' '}
              {totalPlanejadoDesp > 0
                ? diffDesp >= 0
                  ? `Restam ${formatCurrency(diffDesp)}`
                  : `Acima ${formatCurrency(-diffDesp)}`
                : 'Sem plano definido'}
            </p>
            <div className="mb-4">
              <div className="h-2.5 bg-gray-100 rounded-full overflow-hidden relative">
                <div
                  className="h-full rounded-full bg-gray-900 transition-all"
                  style={{ width: `${Math.min(percentualDesp, 100)}%` }}
                />
              </div>
              <div className="flex justify-between mt-1">
                <span className="text-[9px] text-gray-400">R$ 0</span>
                <span className="text-[9px] text-gray-400">{formatCurrency(totalPlanejadoDesp)}</span>
              </div>
            </div>
            <div className="space-y-3.5">
              {goalsDespesas
                .filter((g) => (g.valor_realizado ?? 0) > 0 || (g.valor_planejado ?? 0) > 0)
                .map((cat, idx) => {
                  const realizado = cat.valor_realizado ?? 0
                  const planejado = cat.valor_planejado ?? 0
                  const diff = realizado - planejado
                  const pct = planejado > 0 ? (realizado / planejado) * 100 : 0
                  const isOver = realizado > planejado
                  const color = getGoalColor(cat.grupo, idx)
                  const highlightText =
                    diff >= 0 ? `+${formatCurrency(diff)}` : `-${formatCurrency(-diff)}`
                  const highlightClass =
                    diff > 0
                      ? 'text-red-500 font-semibold'
                      : diff < 0
                        ? 'text-emerald-600 font-semibold'
                        : 'text-gray-500 font-medium'
                  return (
                    <div
                      key={cat.grupo}
                      role="button"
                      tabIndex={0}
                      onClick={() => navegarParaTransacoes(cat.grupo)}
                      onKeyDown={(e) => e.key === 'Enter' && navegarParaTransacoes(cat.grupo)}
                      className="cursor-pointer rounded-xl hover:bg-gray-50 active:bg-gray-100 transition-colors -mx-2 px-2 py-1"
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <div className="flex items-center gap-2 shrink-0 min-w-0">
                          <div
                            className="w-2.5 h-2.5 rounded-full shrink-0"
                            style={{ backgroundColor: color }}
                          />
                          <span className="text-sm text-gray-800 truncate">{cat.grupo}</span>
                        </div>
                        <div className="flex items-center gap-1.5 shrink-0 flex-wrap justify-end">
                          <span className={`text-xs ${highlightClass}`}>{highlightText}</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {formatCurrency(realizado)}
                          </span>
                          <span className="text-[9px] text-gray-400">/ {formatCurrency(planejado)}</span>
                          <ChevronDown className="w-3.5 h-3.5 text-gray-300 -rotate-90" />
                        </div>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full rounded-full transition-all"
                          style={{
                            width: `${Math.min(pct, 100)}%`,
                            backgroundColor: isOver ? '#f87171' : color,
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
            </div>
          </div>
        </>
      )}

      {/* Investimentos vs Plano - Sprint E: fonte = cenário; sem cenário = CTA */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-bold text-gray-900">Investimentos vs Plano</h3>
          <span className="text-sm font-bold text-blue-600">{formatCurrency(totalInvestido)}</span>
        </div>
        {totalPlanejadoInv > 0 ? (
          <>
            <p className="text-[10px] text-gray-400 mb-4">
              Aporte planejado: {formatCurrency(totalPlanejadoInv)}/mês
            </p>
            {(() => {
              const maxVal = Math.max(totalInvestido, totalPlanejadoInv, 1)
              const barMaxH = 120
              const hInvestido = Math.max(8, (totalInvestido / maxVal) * barMaxH)
              const hPlanejado = Math.max(8, (totalPlanejadoInv / maxVal) * barMaxH)
              return (
                <div className="flex items-end gap-3 justify-center py-4 mb-4">
                  <div className="flex flex-col items-center gap-1.5">
                    <span className="text-xs font-bold text-blue-600">{formatCurrency(totalInvestido)}</span>
                    <div
                      className="w-16 bg-blue-500 rounded-t-lg transition-all"
                      style={{ height: hInvestido }}
                    />
                    <span className="text-[10px] text-gray-500">Investido</span>
                  </div>
                  <div className="flex flex-col items-center gap-1.5">
                    <span className="text-xs font-bold text-gray-400">{formatCurrency(totalPlanejadoInv)}</span>
                    <div
                      className="w-16 bg-gray-200 rounded-t-lg border-2 border-dashed border-gray-300 transition-all"
                      style={{ height: hPlanejado }}
                    />
                    <span className="text-[10px] text-gray-500">Planejado</span>
                  </div>
                </div>
              )
            })()}
            {investidoOk && (
              <div className="flex items-center justify-center gap-2 py-3 bg-emerald-50 rounded-xl">
                <span className="text-lg">✅</span>
                <span className="text-xs font-semibold text-emerald-700">
                  {vezesAcimaPlano > 1
                    ? vezesAcimaPlano >= 2
                      ? `${vezesAcimaPlano.toFixed(1).replace('.', ',')}x o plano!`
                      : `${Math.round(pctInvestidoVsPlano)}% do plano!`
                    : 'Aporte do mês realizado 100%!'}
                </span>
              </div>
            )}
          </>
        ) : (
          <Link
            href="/mobile/personalizar-plano"
            className="flex flex-col items-center justify-center gap-3 py-6 px-4 bg-blue-50 border border-blue-100 rounded-xl hover:bg-blue-100 transition-colors"
          >
            <span className="text-2xl">🎯</span>
            <p className="text-sm font-semibold text-blue-900 text-center">
              Crie seu plano de aposentadoria
            </p>
            <p className="text-xs text-blue-700 text-center">
              Defina aporte mensal e acompanhe investimentos vs plano
            </p>
          </Link>
        )}
      </div>
    </div>
  )
}
