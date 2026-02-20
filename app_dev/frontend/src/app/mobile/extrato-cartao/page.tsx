'use client'

/**
 * Extrato do Cartão - Tela dedicada
 * Layout idêntico ao dashboard copy: carousel, resumo, gastos por categoria, transações agrupadas por data
 * Dados: credit-cards API + transactions/list com filtro cartao
 */

import { useState, useEffect, useMemo, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { fetchCreditCards, type CreditCardExpense } from '@/features/dashboard/services/dashboard-api'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { getGoalColor } from '@/features/goals/lib/colors'

const CARD_GRADIENTS = [
  { from: '#dc2626', to: '#991b1b' },
  { from: '#7c3aed', to: '#5b21b6' },
  { from: '#ea580c', to: '#c2410c' },
  { from: '#475569', to: '#1e293b' },
  { from: '#059669', to: '#047857' },
]

interface Transaction {
  id: number
  IdTransacao: string
  Estabelecimento: string
  Valor: number
  Data: string
  GRUPO?: string
  SUBGRUPO?: string
  IdParcela?: string
  TotalParcelas?: number
  NumeroParcela?: number
}

interface CategoryBreakdown {
  grupo: string
  total: number
  pct: number
  color: string
}

function ExtratoCartaoContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const cartaoFromUrl = searchParams.get('cartao')
  const yearFromUrl = searchParams.get('year')
  const monthFromUrl = searchParams.get('month')

  const [cards, setCards] = useState<CreditCardExpense[]>([])
  const [selectedCardIndex, setSelectedCardIndex] = useState(0)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loadingCards, setLoadingCards] = useState(true)
  const [loadingTx, setLoadingTx] = useState(true)
  const [categoryFilter, setCategoryFilter] = useState<string>('all')

  const year = yearFromUrl ? parseInt(yearFromUrl, 10) : new Date().getFullYear()
  const month = monthFromUrl ? parseInt(monthFromUrl, 10) : new Date().getMonth() + 1

  const selectedCard = cards[selectedCardIndex]
  const cartaoAtual = selectedCard?.cartao ?? cartaoFromUrl ?? ''

  useEffect(() => {
    fetchCreditCards(year, month)
      .then((data) => {
        setCards(data)
        if (cartaoFromUrl && data.length > 0) {
          const idx = data.findIndex((c) => c.cartao === cartaoFromUrl)
          if (idx >= 0) setSelectedCardIndex(idx)
        }
      })
      .catch(() => setCards([]))
      .finally(() => setLoadingCards(false))
  }, [year, month, cartaoFromUrl])

  useEffect(() => {
    if (!cartaoAtual) {
      setLoadingTx(false)
      setTransactions([])
      return
    }
    setLoadingTx(true)
    const url = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/list?year=${year}&month=${month}&cartao=${encodeURIComponent(cartaoAtual)}&categoria_geral=Despesa&limit=500`
    fetchWithAuth(url)
      .then((res) => res.json())
      .then((data) => setTransactions(data.transactions || []))
      .catch(() => setTransactions([]))
      .finally(() => setLoadingTx(false))
  }, [cartaoAtual, year, month])

  const categories = useMemo((): CategoryBreakdown[] => {
    const byGrupo: Record<string, number> = {}
    transactions.forEach((t) => {
      const g = t.GRUPO || 'Outros'
      byGrupo[g] = (byGrupo[g] || 0) + Math.abs(t.Valor)
    })
    const total = Object.values(byGrupo).reduce((s, v) => s + v, 0)
    return Object.entries(byGrupo)
      .map(([grupo, totalVal]) => ({
        grupo,
        total: totalVal,
        pct: total > 0 ? Math.round((totalVal / total) * 100) : 0,
        color: getGoalColor(grupo, 0),
      }))
      .sort((a, b) => b.total - a.total)
  }, [transactions])

  const filteredTransactions = useMemo(() => {
    if (categoryFilter === 'all') return transactions
    return transactions.filter((t) => (t.GRUPO || 'Outros') === categoryFilter)
  }, [transactions, categoryFilter])

  const groupedByDate = useMemo(() => {
    const map: Record<string, Transaction[]> = {}
    filteredTransactions.forEach((t) => {
      const key = t.Data || 'Sem data'
      if (!map[key]) map[key] = []
      map[key].push(t)
    })
    return map
  }, [filteredTransactions])

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(v)

  const totalFatura = selectedCard?.total ?? transactions.reduce((s, t) => s + Math.abs(t.Valor), 0)
  const maiorGasto =
    transactions.length > 0
      ? Math.max(...transactions.map((t) => Math.abs(t.Valor)))
      : 0
  const mediaDia = transactions.length > 0 ? Math.round(totalFatura / 30) : 0

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <MobileHeader
        title="Extrato do Cartão"
        leftAction="back"
        onBack={() => router.push('/mobile/dashboard')}
      />

      <div className="flex-1 overflow-y-auto px-4 pb-24 scrollbar-hide">
        {loadingCards ? (
          <div className="py-10 flex justify-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-gray-900" />
          </div>
        ) : cards.length === 0 ? (
          <div className="py-10 text-center text-gray-500">
            <p className="text-sm">Nenhum cartão com gastos no período.</p>
            <Link
              href="/mobile/dashboard"
              className="text-sm text-gray-900 font-medium mt-2 inline-block"
            >
              Voltar ao Dashboard
            </Link>
          </div>
        ) : (
          <>
            {/* Card carousel */}
            <div className="flex gap-3 overflow-x-auto scrollbar-hide py-4 -mx-4 px-4">
              {cards.map((c, idx) => (
                <button
                  key={c.cartao}
                  type="button"
                  onClick={() => setSelectedCardIndex(idx)}
                  className="min-w-[260px] w-[260px] rounded-2xl p-5 text-white shadow-lg cursor-pointer relative overflow-hidden transition-all shrink-0 text-left"
                  style={{
                    background: `linear-gradient(135deg, ${CARD_GRADIENTS[idx % CARD_GRADIENTS.length].from}, ${CARD_GRADIENTS[idx % CARD_GRADIENTS.length].to})`,
                    transform: selectedCardIndex === idx ? 'scale(1.02)' : 'scale(1)',
                  }}
                >
                  <div className="flex items-start justify-between mb-6">
                    <div
                      className="w-8 h-6 rounded"
                      style={{ background: 'linear-gradient(135deg, #d4a853, #c49b47)' }}
                    />
                    <span className="text-[10px] font-bold uppercase tracking-wider opacity-80">
                      {c.cartao}
                    </span>
                  </div>
                  <p className="text-xs opacity-60 mb-0.5">Fatura Atual</p>
                  <p className="text-xl font-bold">{formatCurrency(c.total)}</p>
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-[10px] opacity-60">{c.num_transacoes} transações</span>
                  </div>
                  {selectedCardIndex === idx && (
                    <div className="absolute top-3 right-3 w-5 h-5 rounded-full bg-white/30 flex items-center justify-center">
                      <svg
                        className="w-3 h-3 text-white"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    </div>
                  )}
                </button>
              ))}
            </div>

            {/* Card summary */}
            <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-xs text-gray-500 font-medium">
                    Fatura de{' '}
                    <strong>
                      {['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'][month - 1]}/{year}
                    </strong>
                  </p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatCurrency(totalFatura)}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="bg-gray-50 rounded-xl p-2.5 text-center">
                  <p className="text-[10px] text-gray-500">Transações</p>
                  <p className="text-sm font-bold text-gray-900">{transactions.length}</p>
                </div>
                <div className="bg-gray-50 rounded-xl p-2.5 text-center">
                  <p className="text-[10px] text-gray-500">Maior gasto</p>
                  <p className="text-sm font-bold text-gray-900">
                    {formatCurrency(maiorGasto)}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-xl p-2.5 text-center">
                  <p className="text-[10px] text-gray-500">Média/dia</p>
                  <p className="text-sm font-bold text-gray-900">
                    {formatCurrency(mediaDia)}
                  </p>
                </div>
              </div>
            </div>

            {/* Gastos por categoria */}
            {categories.length > 0 && (
              <div className="bg-white rounded-2xl border border-gray-200 p-5 mb-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                  Gastos por Categoria
                </h3>
                <div className="space-y-3">
                  {categories.map((cat) => (
                    <div key={cat.grupo} className="flex items-center gap-3">
                      <div
                        className="w-4 h-4 rounded-full shrink-0"
                        style={{ backgroundColor: cat.color }}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium text-gray-700">{cat.grupo}</span>
                          <span className="text-xs font-semibold text-gray-900">
                            {formatCurrency(cat.total)}
                          </span>
                        </div>
                        <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full transition-all"
                            style={{
                              width: `${cat.pct}%`,
                              backgroundColor: cat.color,
                            }}
                          />
                        </div>
                      </div>
                      <span className="text-[10px] text-gray-400 w-8 text-right">
                        {cat.pct}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Transações */}
            <div className="mb-2 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-gray-900">Transações</h3>
              <select
                className="text-xs text-gray-500 bg-transparent border-none outline-none cursor-pointer"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="all">Todas</option>
                {categories.map((c) => (
                  <option key={c.grupo} value={c.grupo}>
                    {c.grupo}
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-2">
              {loadingTx ? (
                <div className="py-8 flex justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
                </div>
              ) : Object.keys(groupedByDate).length === 0 ? (
                <div className="py-8 text-center">
                  <p className="text-gray-400 text-sm">Nenhuma transação neste cartão</p>
                </div>
              ) : (
                Object.entries(groupedByDate).map(([date, txList]) => (
                  <div key={date}>
                    <div className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider mt-4 mb-2 ml-1">
                      {date}
                    </div>
                    <div className="bg-white rounded-2xl border border-gray-200 divide-y divide-gray-100">
                      {txList.map((tx) => {
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
                            onClick={() =>
                              router.push(
                                `/mobile/transactions?year=${year}&month=${month}&tx=${tx.IdTransacao}`
                              )
                            }
                            onKeyDown={(e) =>
                              e.key === 'Enter' &&
                              router.push(
                                `/mobile/transactions?year=${year}&month=${month}&tx=${tx.IdTransacao}`
                              )
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
                                {tx.GRUPO || 'Outros'}
                                {parcelaStr && (
                                  <>
                                    {' · '}
                                    <span className="text-amber-600 font-medium">
                                      {parcelaStr}
                                    </span>
                                  </>
                                )}
                              </p>
                            </div>
                            <p className="text-sm font-bold text-gray-900 shrink-0">
                              {formatCurrency(Math.abs(tx.Valor))}
                            </p>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default function ExtratoCartaoPage() {
  return (
    <Suspense
      fallback={
        <div className="flex flex-col h-screen bg-gray-50 items-center justify-center">
          <div className="text-gray-500">Carregando...</div>
        </div>
      }
    >
      <ExtratoCartaoContent />
    </Suspense>
  )
}
