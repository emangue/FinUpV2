'use client'

/**
 * GastosPorCartaoBox - Seção "Gastos por Cartão" na aba Resultado > Despesas
 * Layout idêntico ao dashboard copy: carousel de cartões, detalhe selecionado, resumo geral
 * Dados da API credit-cards (cartao, total, percentual, num_transacoes)
 * Sem limite/fecha/vence/status (não existem no backend)
 */

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { CreditCard } from 'lucide-react'
import { ChevronRight } from 'lucide-react'
import { fetchCreditCards, type CreditCardExpense } from '../services/dashboard-api'

const CARD_GRADIENTS = [
  'bg-gradient-to-br from-red-600 to-red-800',
  'bg-gradient-to-br from-violet-600 to-violet-800',
  'bg-gradient-to-br from-orange-600 to-orange-700',
  'bg-gradient-to-br from-slate-600 to-slate-800',
  'bg-gradient-to-br from-emerald-600 to-emerald-800',
]

const CARD_DOT_COLORS = [
  'bg-red-500',
  'bg-violet-500',
  'bg-orange-500',
  'bg-slate-500',
  'bg-emerald-500',
]

function getCardStyle(index: number) {
  return {
    gradient: CARD_GRADIENTS[index % CARD_GRADIENTS.length],
    dotColor: CARD_DOT_COLORS[index % CARD_DOT_COLORS.length],
  }
}

function extractLastDigits(cartao: string): string {
  const match = cartao.match(/\d{4}$/)
  return match ? match[0] : '****'
}

interface GastosPorCartaoBoxProps {
  year: number
  month?: number
  monthLabel?: string
}

export function GastosPorCartaoBox({ year, month, monthLabel }: GastosPorCartaoBoxProps) {
  const [cards, setCards] = useState<CreditCardExpense[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedIndex, setSelectedIndex] = useState(0)

  useEffect(() => {
    fetchCreditCards(year, month)
      .then(setCards)
      .catch(() => setCards([]))
      .finally(() => setLoading(false))
  }, [year, month])

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    }).format(v)

  if (loading) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-4 mb-6">
        <div className="flex items-center gap-2 text-gray-500 mb-4">
          <CreditCard className="w-4 h-4" />
          <h3 className="text-sm font-semibold text-gray-900">Gastos por Cartão</h3>
        </div>
        <div className="h-32 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900" />
        </div>
      </div>
    )
  }

  if (cards.length === 0) {
    return null
  }

  const totalGeral = cards.reduce((s, c) => s + c.total, 0)
  const currentCard = cards[selectedIndex]
  const { gradient, dotColor } = getCardStyle(selectedIndex)

  const extratoUrl = `/mobile/extrato-cartao?cartao=${encodeURIComponent(currentCard.cartao)}&year=${year}&month=${month ?? ''}`

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <CreditCard className="w-4 h-4 text-gray-500" />
          Gastos por Cartão
        </h3>
        <span className="text-xs text-gray-400 font-medium">
          {monthLabel ?? (month ? `${String(month).padStart(2, '0')}/${year}` : `${year}`)}
        </span>
      </div>

      {/* Card carousel */}
      <div className="flex gap-3 overflow-x-auto pb-4 scrollbar-hide mb-4">
        {cards.map((card, i) => {
          const style = getCardStyle(i)
          return (
            <button
              key={card.cartao}
              type="button"
              onClick={() => setSelectedIndex(i)}
              className={`${style.gradient} rounded-2xl p-4 min-w-[220px] h-[130px] flex flex-col justify-between text-white shadow-lg shrink-0 cursor-pointer hover:scale-[1.02] transition-transform text-left ${
                i === selectedIndex ? 'outline outline-3 outline-white/80 -outline-offset-3' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div
                  className="w-8 h-6 rounded"
                  style={{ background: 'linear-gradient(135deg, #fbbf24, #f59e0b, #d97706)' }}
                />
                <span className="text-[10px] font-bold tracking-wider opacity-90">••••</span>
              </div>
              <div>
                <p className="text-[10px] opacity-70 tracking-widest mb-1">
                  •••• •••• •••• {extractLastDigits(card.cartao)}
                </p>
                <div className="flex items-end justify-between">
                  <p className="text-xs opacity-90 truncate max-w-[140px]">{card.cartao}</p>
                  <p className="text-sm font-bold shrink-0">{formatCurrency(card.total)}</p>
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Selected card details */}
      <div className="border-t border-gray-100 pt-4">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-sm font-semibold text-gray-900">{currentCard.cartao}</p>
            <p className="text-xs text-gray-500">
              {currentCard.num_transacoes} transações
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-gray-900">
              {formatCurrency(currentCard.total)}
            </p>
            <p className="text-xs text-gray-400">fatura atual</p>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">{currentCard.percentual.toFixed(1)}% do total</span>
          <Link
            href={extratoUrl}
            className="text-xs text-gray-500 hover:text-gray-900 font-medium flex items-center gap-1 no-underline"
          >
            Ver extrato
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Summary all cards */}
      <div className="border-t border-gray-100 mt-4 pt-4">
        <div className="flex items-center justify-between mb-3">
          <p className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
            Resumo Geral
          </p>
          <p className="text-sm font-bold text-gray-900">
            {formatCurrency(totalGeral)}
          </p>
        </div>
        <div className="space-y-2.5">
          {cards.map((card, i) => {
            const style = getCardStyle(i)
            const pct = totalGeral > 0 ? (card.total / totalGeral) * 100 : 0
            return (
              <div key={card.cartao}>
                <div className="flex items-center justify-between mb-0.5">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${style.dotColor}`} />
                    <span className="text-xs text-gray-700 truncate max-w-[180px]">
                      {card.cartao}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs font-semibold text-gray-900">
                      {formatCurrency(card.total)}
                    </span>
                    <span className="text-[10px] text-gray-400">{pct.toFixed(1)}%</span>
                  </div>
                </div>
                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${style.dotColor}`}
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
