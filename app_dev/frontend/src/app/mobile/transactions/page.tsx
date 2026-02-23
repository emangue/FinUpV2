'use client'

/**
 * Transactions Mobile - Tela de Transações (Sprint F Redesign)
 *
 * - Sem MonthScrollPicker: exibe todas as transações (período configurável)
 * - Caixa Resumo: total, qtd, maior gasto, média/dia (atualiza com filtros)
 * - Gastos por Grupo: collapse, atualiza com filtros
 * - Busca: texto único, tempo real (estabelecimento, grupo, subgrupo, data)
 * - Filtros avançados: período, grupo, subgrupo, estabelecimento, categoria_geral
 * - Lista: agrupada por data, layout extrato-cartão, sinal+cor valor
 */

import * as React from 'react'
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ChevronDown, ChevronUp, Filter, Plus, Search } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { cn } from '@/lib/utils'
import { TransactionDetailBottomSheet } from '@/components/mobile/transaction-detail-bottom-sheet'
import { getGoalColor } from '@/features/goals/lib/colors'

const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

interface Transaction {
  id: number
  IdTransacao: string
  Estabelecimento: string
  Valor: number
  Data: string
  GRUPO?: string
  SUBGRUPO?: string
  Grupo?: string
  Subgrupo?: string
  CategoriaGeral?: string
  IdParcela?: string
  TotalParcelas?: number
  NumeroParcela?: number
  origem_classificacao?: string
  MesFatura?: string
  NomeCartao?: string
}

interface Resumo {
  total: number
  quantidade: number
  maior_gasto: number
  media_por_dia: number
}

interface GastosPorGrupo {
  grupo: string
  total: number
}

interface GrupoSubgrupoOption {
  grupo: string
  subgrupo: string | null
  total_transacoes: number
}

function buildQueryParams(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v != null && v !== '') {
      search.set(k, String(v))
    }
  })
  return search.toString()
}

function TransactionsMobileContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const fromMetas = searchParams.get('from') === 'metas'
  const urlGoalId = searchParams.get('goalId')
  const urlGrupo = searchParams.get('grupo')
  const urlSubgrupo = searchParams.get('subgrupo')

  const now = new Date()
  const [semFiltroPeriodo, setSemFiltroPeriodo] = useState(true)
  const [yearInicio, setYearInicio] = useState(now.getFullYear())
  const [monthInicio, setMonthInicio] = useState(1)
  const [yearFim, setYearFim] = useState(now.getFullYear())
  const [monthFim, setMonthFim] = useState(now.getMonth() + 1)

  const [searchQuery, setSearchQuery] = useState('')
  const [searchDebounced, setSearchDebounced] = useState('')
  const [categoriaGeral, setCategoriaGeral] = useState<string>('')
  const [grupoFilter, setGrupoFilter] = useState(urlGrupo || '')
  const [subgrupoFilter, setSubgrupoFilter] = useState(urlSubgrupo === '__null__' ? '' : (urlSubgrupo || ''))
  const [estabelecimentoFilter, setEstabelecimentoFilter] = useState('')

  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [resumo, setResumo] = useState<Resumo | null>(null)
  const [gastosPorGrupo, setGastosPorGrupo] = useState<GastosPorGrupo[]>([])
  const [gruposOptions, setGruposOptions] = useState<GrupoSubgrupoOption[]>([])
  const [loading, setLoading] = useState(true)
  const [resumoLoading, setResumoLoading] = useState(true)
  const [gastosLoading, setGastosLoading] = useState(false)
  const [selectedTransaction, setSelectedTransaction] = useState<Transaction | null>(null)
  const [detailSheetOpen, setDetailSheetOpen] = useState(false)
  const [gastosOpen, setGastosOpen] = useState(false)
  const [filtrosOpen, setFiltrosOpen] = useState(false)

  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(() => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current)
    searchTimeoutRef.current = setTimeout(() => {
      setSearchDebounced(searchQuery)
    }, 300)
    return () => {
      if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current)
    }
  }, [searchQuery])

  const filters = useMemo(() => {
    const base: Record<string, string | number | boolean | undefined | null> = {
      search: searchDebounced || undefined,
      categoria_geral: categoriaGeral || undefined,
      grupo: grupoFilter || undefined,
      subgrupo: subgrupoFilter === '__null__' ? undefined : (subgrupoFilter || undefined),
      subgrupo_null: subgrupoFilter === '__null__' ? true : undefined,
      estabelecimento: estabelecimentoFilter || undefined,
    }
    if (!semFiltroPeriodo) {
      const isSingleMonth = yearInicio === yearFim && monthInicio === monthFim
      if (isSingleMonth) {
        base.year = yearInicio
        base.month = monthInicio
      } else {
        base.year_inicio = yearInicio
        base.month_inicio = monthInicio
        base.year_fim = yearFim
        base.month_fim = monthFim
      }
    }
    return base
  }, [semFiltroPeriodo, yearInicio, monthInicio, yearFim, monthFim, searchDebounced, categoriaGeral, grupoFilter, subgrupoFilter, estabelecimentoFilter])

  const fetchTransactions = useCallback(async () => {
    const BASE = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions`
    const q = buildQueryParams({
      ...filters,
      limit: 500,
      page: 1,
    })
    try {
      setLoading(true)
      const res = await fetchWithAuth(`${BASE}/list?${q}`)
      if (res.status === 401) {
        router.push('/login')
        return
      }
      const data = await res.json()
      setTransactions(data.transactions || [])
    } catch {
      setTransactions([])
    } finally {
      setLoading(false)
    }
  }, [filters, router])

  const fetchResumo = useCallback(async () => {
    const BASE = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions`
    const q = buildQueryParams(filters)
    try {
      setResumoLoading(true)
      const res = await fetchWithAuth(`${BASE}/resumo?${q}`)
      if (res.ok) {
        const data = await res.json()
        setResumo(data)
      } else {
        setResumo(null)
      }
    } catch {
      setResumo(null)
    } finally {
      setResumoLoading(false)
    }
  }, [filters])

  const fetchGastosPorGrupo = useCallback(async () => {
    const BASE = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions`
    const q = buildQueryParams(filters)
    try {
      setGastosLoading(true)
      const res = await fetchWithAuth(`${BASE}/gastos-por-grupo?${q}`)
      if (res.ok) {
        const data = await res.json()
        setGastosPorGrupo(Array.isArray(data) ? data : [])
      } else {
        setGastosPorGrupo([])
      }
    } catch {
      setGastosPorGrupo([])
    } finally {
      setGastosLoading(false)
    }
  }, [filters])

  const fetchGruposOptions = useCallback(async () => {
    try {
      const res = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/migration/grupos-subgrupos`
      )
      if (res.ok) {
        const data = await res.json()
        setGruposOptions(data.opcoes || [])
      }
    } catch {
      setGruposOptions([])
    }
  }, [])

  useEffect(() => {
    fetchTransactions()
    fetchResumo()
  }, [fetchTransactions, fetchResumo])

  useEffect(() => {
    if (gastosOpen) fetchGastosPorGrupo()
  }, [gastosOpen, fetchGastosPorGrupo])

  useEffect(() => {
    if (filtrosOpen) fetchGruposOptions()
  }, [filtrosOpen, fetchGruposOptions])

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(v)

  const groupedByDate = useMemo(() => {
    const map: Record<string, Transaction[]> = {}
    transactions.forEach((t) => {
      const key = t.Data || 'Sem data'
      if (!map[key]) map[key] = []
      map[key].push(t)
    })
    return map
  }, [transactions])

  const sortedDateKeys = useMemo(() => {
    const keys = Object.keys(groupedByDate)
    return keys.sort((a, b) => {
      const parse = (s: string) => {
        if (s === 'Sem data') return '00000000'
        const [d, m, y] = s.split('/')
        if (d && m && y) return `${y}${m.padStart(2, '0')}${d.padStart(2, '0')}`
        return '00000000'
      }
      return parse(b).localeCompare(parse(a))
    })
  }, [groupedByDate])

  const subgruposForGrupo = useMemo(() => {
    if (!grupoFilter) return []
    const opts = gruposOptions.filter((o) => o.grupo === grupoFilter)
    const hasNull = opts.some((o) => !o.subgrupo)
    const subs = [...new Set(opts.map((o) => o.subgrupo).filter(Boolean))] as string[]
    const sorted = subs.sort()
    return hasNull ? ['__null__', ...sorted] : sorted
  }, [gruposOptions, grupoFilter])

  const totalGastos = gastosPorGrupo.reduce((s, g) => s + g.total, 0)

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <MobileHeader
        title={urlGrupo ? `${urlGrupo}${urlSubgrupo && urlSubgrupo !== '__null__' ? ` › ${urlSubgrupo}` : ''}` : 'Transações'}
        leftAction={fromMetas ? 'back' : null}
        onBack={
          fromMetas
            ? () => {
                const target = urlGoalId ? `/mobile/budget/${urlGoalId}` : '/mobile/budget'
                router.push(target)
              }
            : undefined
        }
      />

      {/* Busca */}
      <div className="px-4 py-3 bg-white border-b border-gray-200">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" aria-hidden />
          <input
            type="search"
            placeholder="Buscar estabelecimento, grupo, data..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-gray-100 rounded-xl text-base text-gray-900 placeholder-gray-500 border-0 focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all"
            aria-label="Buscar transações"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 pb-24 scrollbar-hide">
        {/* Resumo - Layout Fatura (como extrato-cartão) */}
        <div className="bg-white rounded-2xl border border-gray-200 p-5 mt-4 mb-4">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-xs text-gray-500 font-medium">
                {semFiltroPeriodo ? (
                  'Todas as transações'
                ) : yearInicio === yearFim && monthInicio === monthFim ? (
                  <>
                    Resumo de{' '}
                    <strong>
                      {MESES[monthInicio - 1]}/{yearInicio}
                    </strong>
                  </>
                ) : (
                  <>
                    Período{' '}
                    <strong>
                      {MESES[monthInicio - 1]}/{yearInicio} a {MESES[monthFim - 1]}/{yearFim}
                    </strong>
                  </>
                )}
              </p>
              {resumoLoading ? (
                <div className="h-8 w-8 mt-1 animate-pulse bg-gray-100 rounded" />
              ) : resumo ? (
                <p className={cn('text-2xl font-bold mt-1', resumo.total >= 0 ? 'text-green-600' : 'text-red-600')}>
                  {resumo.total >= 0 ? '+' : ''}{formatCurrency(resumo.total)}
                </p>
              ) : (
                <p className="text-2xl font-bold text-gray-900 mt-1">R$ 0,00</p>
              )}
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-gray-50 rounded-xl p-2.5 text-center">
              <p className="text-[10px] text-gray-500">Transações</p>
              <p className="text-sm font-bold text-gray-900">{resumo?.quantidade ?? 0}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-2.5 text-center">
              <p className="text-[10px] text-gray-500">Maior gasto</p>
              <p className="text-sm font-bold text-gray-900">{formatCurrency(resumo?.maior_gasto ?? 0)}</p>
            </div>
            <div className="bg-gray-50 rounded-xl p-2.5 text-center">
              <p className="text-[10px] text-gray-500">Média/dia</p>
              <p className="text-sm font-bold text-gray-900">{formatCurrency(resumo?.media_por_dia ?? 0)}</p>
            </div>
          </div>
        </div>

        {/* Gastos por Grupo */}
        <div className="bg-white rounded-2xl border border-gray-200 mt-4 overflow-hidden">
          <button
            type="button"
            onClick={() => setGastosOpen(!gastosOpen)}
            className="w-full flex items-center justify-between p-4 text-left"
          >
            <h3 className="text-sm font-semibold text-gray-900">Gastos por Categoria</h3>
            {gastosOpen ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
          </button>
          {gastosOpen && (
            <div className="px-4 pb-4">
              {gastosLoading ? (
                <div className="h-16 flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-gray-900" />
                </div>
              ) : gastosPorGrupo.length > 0 ? (
                <div className="space-y-3">
                  {gastosPorGrupo.map((cat) => {
                    const pct = totalGastos > 0 ? Math.round((cat.total / totalGastos) * 100) : 0
                    const color = getGoalColor(cat.grupo, 0)
                    return (
                      <div key={cat.grupo} className="flex items-center gap-3">
                        <div className="w-4 h-4 rounded-full shrink-0" style={{ backgroundColor: color }} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-xs font-medium text-gray-700">{cat.grupo}</span>
                            <span className="text-xs font-semibold text-gray-900">{formatCurrency(cat.total)}</span>
                          </div>
                          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full transition-all"
                              style={{ width: `${pct}%`, backgroundColor: color }}
                            />
                          </div>
                        </div>
                        <span className="text-[10px] text-gray-400 w-8 text-right">{pct}%</span>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <p className="text-sm text-gray-400 py-2">Nenhum gasto no período</p>
              )}
            </div>
          )}
        </div>

        {/* Filtros Avançados */}
        <div className="bg-white rounded-2xl border border-gray-200 mt-4 overflow-hidden">
          <button
            type="button"
            onClick={() => setFiltrosOpen(!filtrosOpen)}
            className="w-full flex items-center justify-between p-4 text-left"
          >
            <span className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <h3 className="text-sm font-semibold text-gray-900">Filtros</h3>
            </span>
            {filtrosOpen ? <ChevronUp className="w-5 h-5 text-gray-400" /> : <ChevronDown className="w-5 h-5 text-gray-400" />}
          </button>
          {filtrosOpen && (
            <div className="px-4 pb-4 space-y-3">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={semFiltroPeriodo}
                  onChange={(e) => setSemFiltroPeriodo(e.target.checked)}
                  className="rounded border-gray-300"
                />
                <span className="text-sm text-gray-700">Todas as transações (sem filtro de período)</span>
              </label>
              {!semFiltroPeriodo && (
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-gray-500 block mb-1">De</label>
                  <div className="flex gap-1">
                    <select
                      value={monthInicio}
                      onChange={(e) => setMonthInicio(Number(e.target.value))}
                      className="flex-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5"
                    >
                      {MESES.map((m, i) => (
                        <option key={m} value={i + 1}>
                          {m}
                        </option>
                      ))}
                    </select>
                    <select
                      value={yearInicio}
                      onChange={(e) => setYearInicio(Number(e.target.value))}
                      className="w-20 text-sm border border-gray-200 rounded-lg px-2 py-1.5"
                    >
                      {[now.getFullYear(), now.getFullYear() - 1, now.getFullYear() - 2].map((y) => (
                        <option key={y} value={y}>
                          {y}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-[10px] text-gray-500 block mb-1">Até</label>
                  <div className="flex gap-1">
                    <select
                      value={monthFim}
                      onChange={(e) => setMonthFim(Number(e.target.value))}
                      className="flex-1 text-sm border border-gray-200 rounded-lg px-2 py-1.5"
                    >
                      {MESES.map((m, i) => (
                        <option key={m} value={i + 1}>
                          {m}
                        </option>
                      ))}
                    </select>
                    <select
                      value={yearFim}
                      onChange={(e) => setYearFim(Number(e.target.value))}
                      className="w-20 text-sm border border-gray-200 rounded-lg px-2 py-1.5"
                    >
                      {[now.getFullYear(), now.getFullYear() - 1, now.getFullYear() - 2].map((y) => (
                        <option key={y} value={y}>
                          {y}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
              )}
              <div>
                <label className="text-[10px] text-gray-500 block mb-1">Categoria geral</label>
                <select
                  value={categoriaGeral}
                  onChange={(e) => setCategoriaGeral(e.target.value)}
                  className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
                >
                  <option value="">Todas</option>
                  <option value="Receita">Receita</option>
                  <option value="Despesa">Despesa</option>
                  <option value="Investimentos">Investimentos</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] text-gray-500 block mb-1">Grupo</label>
                <select
                  value={grupoFilter}
                  onChange={(e) => {
                    setGrupoFilter(e.target.value)
                    setSubgrupoFilter('')
                  }}
                  className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
                >
                  <option value="">Todos</option>
                  {[...new Set(gruposOptions.map((o) => o.grupo))].sort().map((g) => (
                    <option key={g} value={g}>
                      {g}
                    </option>
                  ))}
                </select>
              </div>
              {grupoFilter && subgruposForGrupo.length > 0 && (
                <div>
                  <label className="text-[10px] text-gray-500 block mb-1">Subgrupo</label>
                  <select
                    value={subgrupoFilter}
                    onChange={(e) => setSubgrupoFilter(e.target.value)}
                    className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
                  >
                    <option value="">Todos</option>
                    {subgruposForGrupo.map((s) => (
                      <option key={s} value={s}>
                        {s === '__null__' ? 'Sem subgrupo' : s}
                      </option>
                    ))}
                  </select>
                </div>
              )}
              <div>
                <label className="text-[10px] text-gray-500 block mb-1">Estabelecimento</label>
                <input
                  type="text"
                  value={estabelecimentoFilter}
                  onChange={(e) => setEstabelecimentoFilter(e.target.value)}
                  placeholder="Filtrar por nome"
                  className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2"
                />
              </div>
            </div>
          )}
        </div>

        {/* Lista de transações */}
        <div className="mt-4 mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-gray-900">Transações</h3>
        </div>

        {loading ? (
          <div className="py-10 flex justify-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-900" />
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10">
            <p className="text-gray-400 text-center mb-4">
              {searchQuery.trim() ? `Nenhuma transação encontrada para "${searchQuery}"` : 'Nenhuma transação no período.'}
            </p>
            {!searchQuery.trim() && (
              <button
                onClick={() => router.push('/mobile/upload')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Importar Arquivo
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            {sortedDateKeys.map((date) => {
              const txList = groupedByDate[date]
              return (
                <div key={date}>
                  <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mt-4 mb-2 ml-1">
                    {date}
                  </div>
                  <div className="bg-white rounded-2xl border border-gray-200 divide-y divide-gray-100">
                    {txList.map((tx) => {
                      const grupo = tx.GRUPO ?? tx.Grupo ?? 'Outros'
                      const isIncome = tx.Valor > 0
                      const parcelaStr =
                        tx.IdParcela && tx.TotalParcelas && tx.NumeroParcela
                          ? `${tx.NumeroParcela}/${tx.TotalParcelas}`
                          : undefined
                      return (
                        <div
                          key={tx.id}
                          className="flex items-center gap-3 px-4 py-3.5"
                          role="button"
                          tabIndex={0}
                          onClick={() => {
                            setSelectedTransaction(tx)
                            setDetailSheetOpen(true)
                          }}
                          onKeyDown={(e) =>
                            e.key === 'Enter' && (setSelectedTransaction(tx), setDetailSheetOpen(true))
                          }
                        >
                          <div className="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center text-lg shrink-0">
                            💳
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-gray-900 truncate">
                              {tx.Estabelecimento}
                            </p>
                            <p className="text-xs text-gray-400 mt-0.5">
                              {grupo}
                              {parcelaStr && (
                                <>
                                  {' · '}
                                  <span className="text-amber-600 font-medium">{parcelaStr}</span>
                                </>
                              )}
                            </p>
                          </div>
                          <p
                            className={cn(
                              'text-sm font-bold shrink-0',
                              isIncome ? 'text-green-600' : 'text-red-600'
                            )}
                          >
                            {isIncome ? '+' : '-'}{formatCurrency(Math.abs(tx.Valor))}
                          </p>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <TransactionDetailBottomSheet
        isOpen={detailSheetOpen}
        onClose={() => {
          setDetailSheetOpen(false)
          setSelectedTransaction(null)
        }}
        transaction={selectedTransaction}
        onSaved={() => {
          fetchTransactions()
          fetchResumo()
          if (gastosOpen) fetchGastosPorGrupo()
        }}
      />

      <button
        onClick={() => {}}
        className="fixed bottom-24 right-5 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition-all active:scale-95"
        style={{ boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)' }}
        aria-label="Nova transação"
      >
        <Plus className="w-6 h-6" />
      </button>
    </div>
  )
}

export default function TransactionsMobilePage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col h-screen bg-gray-50 items-center justify-center">
          <div className="text-gray-500">Carregando...</div>
        </div>
      }
    >
      <TransactionsMobileContent />
    </Suspense>
  )
}
