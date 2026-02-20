'use client'

/**
 * InvestmentCard - Card de investimento para mobile
 * Layout inspirado em listas de vagas: ícone, título, subtítulo, valor, tags
 */

import * as React from 'react'
import { ChevronRight, Pencil } from 'lucide-react'
import type { InvestimentoPortfolio } from '../../types'

interface InvestmentCardProps {
  investment: InvestimentoPortfolio
  onClick?: () => void
  /** Abre sheet para editar valor do mês (patrimônio) */
  onEditValor?: () => void
}

function getTipoColor(tipo: string, index: number): string {
  const hash = tipo.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  const colors = [
    'bg-blue-500',
    'bg-emerald-500',
    'bg-amber-500',
    'bg-violet-500',
    'bg-rose-500',
    'bg-cyan-500',
    'bg-indigo-500',
  ]
  return colors[(hash + index) % colors.length]
}

export function InvestmentCard({ investment, onClick, onEditValor }: InvestmentCardProps) {
  const formatCurrency = (value: string | number) => {
    const num = typeof value === 'string' ? parseFloat(value) : value
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(num || 0)
  }

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return null
    try {
      const d = new Date(dateStr)
      return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
    } catch {
      return null
    }
  }

  // Usar valores do histórico do mês (mesma fonte de ativos/passivos) quando disponível
  const valorTotal = investment.valor_total_mes != null
    ? (typeof investment.valor_total_mes === 'number' ? investment.valor_total_mes : parseFloat(String(investment.valor_total_mes)) || 0)
    : parseFloat(investment.valor_total_inicial || '0')
  let valorUnitario = investment.valor_unitario_mes != null
    ? (typeof investment.valor_unitario_mes === 'number' ? investment.valor_unitario_mes : parseFloat(String(investment.valor_unitario_mes)) || 0)
    : parseFloat(investment.valor_unitario_inicial || '0')
  const quantidade = investment.quantidade_mes ?? investment.quantidade ?? 1
  if (valorTotal !== 0 && (valorUnitario === 0 || !valorUnitario)) {
    valorUnitario = valorTotal / (quantidade || 1)
  }
  const colorClass = getTipoColor(investment.tipo_investimento, investment.id)

  return (
    <div className="w-full bg-gray-50 hover:bg-gray-100 rounded-xl p-4 border border-gray-100 transition-colors flex gap-4 items-start">
      <button
        type="button"
        onClick={onClick}
        className="flex-1 flex gap-4 text-left min-w-0 active:scale-[0.99]"
      >
        {/* Ícone/Logo - círculo colorido */}
        <div
          className={`w-12 h-12 rounded-xl ${colorClass} flex items-center justify-center shrink-0`}
        >
          <span className="text-white font-bold text-sm">
            {investment.nome_produto.charAt(0).toUpperCase()}
          </span>
        </div>

        {/* Conteúdo principal */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">
            {investment.nome_produto}
          </h3>
          <p className="text-sm text-gray-500 mt-0.5">
            {investment.tipo_investimento}
            {investment.corretora && ` • ${investment.corretora}`}
          </p>

          {/* Valor total em destaque */}
          <p className="font-bold text-gray-900 mt-2 text-base">
            {formatCurrency(valorTotal)}
          </p>

          {/* Tags: %CDI, data, quantidade */}
          <div className="flex flex-wrap gap-2 mt-2">
            {investment.percentual_cdi != null && investment.percentual_cdi > 0 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-green-100 text-green-800">
                {investment.percentual_cdi}% CDI
              </span>
            )}
            {formatDate(investment.data_aplicacao) && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-gray-200 text-gray-700">
                {formatDate(investment.data_aplicacao)}
              </span>
            )}
            <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-blue-100 text-blue-800">
              {quantidade} un. × {formatCurrency(valorUnitario)}
            </span>
          </div>
        </div>
      </button>

      {/* Ações: editar valor | detalhes */}
      <div className="flex items-center gap-1 shrink-0">
        {onEditValor && (
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); onEditValor() }}
            className="p-2 rounded-full hover:bg-gray-200 text-gray-500 hover:text-indigo-600"
            aria-label="Atualizar valor"
          >
            <Pencil className="w-4 h-4" />
          </button>
        )}
        <button
          type="button"
          onClick={onClick}
          className="p-2 rounded-full hover:bg-gray-200 text-gray-400"
          aria-label="Ver detalhes"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  )
}
