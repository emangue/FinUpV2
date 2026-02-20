'use client'

/**
 * DistribuicaoLista - Lista de distribuição por tipo_investimento
 * Dados vêm da API /investimentos/distribuicao-tipo?classe_ativo=Ativo|Passivo
 * Backend usa classe_ativo e tipo_investimento da base investimentos_portfolio/historico
 */

import { Badge } from '@/components/ui/badge'
import type { DistribuicaoTipo } from '@/features/investimentos/types'

interface DistribuicaoListaProps {
  distribuicao: DistribuicaoTipo[]
  totalGeral: number
  isPassivo?: boolean
  /** Ao clicar em um item, navega para a tela de investimentos (ex: filtrado por tipo) */
  onItemClick?: (tipo: string) => void
}

const BAR_COLORS = [
  'bg-blue-500',
  'bg-green-500',
  'bg-purple-500',
  'bg-orange-500',
  'bg-pink-500',
  'bg-teal-500',
  'bg-indigo-500',
  'bg-amber-500',
  'bg-rose-500',
  'bg-slate-600',
]

function getTipoColor(tipo: string, index: number) {
  const hash = tipo.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0)
  return BAR_COLORS[(hash + index) % BAR_COLORS.length]
}

export function DistribuicaoLista({
  distribuicao,
  totalGeral,
  isPassivo = false,
  onItemClick,
}: DistribuicaoListaProps) {
  const formatCurrency = (value: string | number) => {
    const num = typeof value === 'string' ? parseFloat(value) : value
    const absNum = Math.abs(num)
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(isPassivo ? -absNum : absNum)
  }

  const getPercentual = (valor: string | number) => {
    if (totalGeral <= 0) return 0
    const num = Math.abs(typeof valor === 'number' ? valor : parseFloat(String(valor)) || 0)
    return (num / Math.abs(totalGeral)) * 100
  }

  const toNum = (v: string | number) => Math.abs(typeof v === 'number' ? v : parseFloat(String(v)) || 0)
  const ordenada = [...distribuicao].sort(
    (a, b) => toNum(b.total_investido) - toNum(a.total_investido)
  )
  const maxValor = ordenada.length > 0 ? toNum(ordenada[0].total_investido) : 0

  if (ordenada.length === 0) {
    return (
      <div className="rounded-xl border border-gray-200 bg-white p-6 text-center text-gray-500">
        <p className="text-sm">
          Nenhum {isPassivo ? 'passivo' : 'ativo'} cadastrado.
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4">
      <div className="space-y-4">
        {ordenada.map((item, index) => {
          const valorAbs = toNum(item.total_investido)
          const percentual = getPercentual(item.total_investido)
          const larguraBarra =
            maxValor > 0 ? (valorAbs / maxValor) * 100 : 0
          const colorClass = getTipoColor(item.tipo, index)

          return (
            <button
              key={`${item.tipo}-${index}`}
              type="button"
              onClick={() => onItemClick?.(item.tipo)}
              className={`w-full text-left space-y-2 rounded-lg p-2 -mx-2 transition-colors ${
                onItemClick ? 'hover:bg-gray-50 active:bg-gray-100 cursor-pointer' : ''
              }`}
            >
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className={`w-3 h-3 rounded-full ${colorClass}`}
                  />
                  <span className="font-medium">{item.tipo}</span>
                  <Badge variant="outline" className="text-xs">
                    {item.quantidade}{' '}
                    {item.quantidade === 1
                      ? isPassivo
                        ? 'passivo'
                        : 'ativo'
                      : isPassivo
                        ? 'passivos'
                        : 'ativos'}
                  </Badge>
                </div>
                <span className="font-semibold">{percentual.toFixed(1)}%</span>
              </div>
              <div className="relative h-8 bg-gray-100 rounded-md overflow-hidden flex items-center">
                <div
                  className={`h-full ${colorClass} opacity-80`}
                  style={{ width: `${larguraBarra}%` }}
                />
                <span className="absolute right-3 text-xs font-semibold text-gray-900">
                  {formatCurrency(item.total_investido)}
                </span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
