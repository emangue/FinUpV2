'use client'

/**
 * Sheet para editar valor do mês (patrimônio) - fluxo: copiar mês anterior → atualizar valor
 */

import * as React from 'react'
import { X, Loader2 } from 'lucide-react'
import { updateHistoricoMes } from '../../services/investimentos-api'
import type { InvestimentoPortfolio } from '../../types'

interface EditValorMesSheetProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
  investment: InvestimentoPortfolio | null
  anomes: number
  mesLabel: string
}

export function EditValorMesSheet({
  open,
  onClose,
  onSuccess,
  investment,
  anomes,
  mesLabel,
}: EditValorMesSheetProps) {
  const valorTotal = investment?.valor_total_mes != null
    ? (typeof investment.valor_total_mes === 'number'
        ? investment.valor_total_mes
        : parseFloat(String(investment.valor_total_mes)) || 0)
    : parseFloat(investment?.valor_total_inicial || '0') || 0
  const quantidade = investment?.quantidade_mes ?? investment?.quantidade ?? 1
  let valorUnitario = investment?.valor_unitario_mes != null
    ? (typeof investment.valor_unitario_mes === 'number'
        ? investment.valor_unitario_mes
        : parseFloat(String(investment.valor_unitario_mes)) || 0)
    : parseFloat(investment?.valor_unitario_inicial || '0') || 0
  if (valorTotal !== 0 && (valorUnitario === 0 || !valorUnitario)) {
    valorUnitario = valorTotal / (quantidade || 1)
  }

  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [valorTotalInput, setValorTotalInput] = React.useState('')
  const [quantidadeInput, setQuantidadeInput] = React.useState('')
  const [valorUnitarioInput, setValorUnitarioInput] = React.useState('')

  React.useEffect(() => {
    if (open && investment) {
      setValorTotalInput(String(valorTotal))
      setQuantidadeInput(String(quantidade))
      setValorUnitarioInput(String(valorUnitario))
      setError(null)
    }
  }, [open, investment, valorTotal, quantidade, valorUnitario])

  const handleValorTotalChange = (v: string) => {
    setValorTotalInput(v)
    const total = parseFloat(v.replace(',', '.')) || 0
    const q = parseFloat(quantidadeInput.replace(',', '.')) || 1
    if (total > 0 && q > 0) {
      setValorUnitarioInput((total / q).toFixed(2))
    }
  }

  const handleQuantidadeChange = (v: string) => {
    setQuantidadeInput(v)
    const total = parseFloat(valorTotalInput.replace(',', '.')) || 0
    const q = parseFloat(v.replace(',', '.')) || 1
    if (total > 0 && q > 0) {
      setValorUnitarioInput((total / q).toFixed(2))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!investment) return

    const total = parseFloat(valorTotalInput.replace(',', '.')) || 0
    const qty = parseFloat(quantidadeInput.replace(',', '.')) || 1
    const unit = parseFloat(valorUnitarioInput.replace(',', '.')) || (total / qty)

    setLoading(true)
    setError(null)
    try {
      await updateHistoricoMes(investment.id, anomes, {
        valor_total: total,
        quantidade: qty,
        valor_unitario: unit,
      })
      onSuccess()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao atualizar valor')
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <>
      <div
        className="fixed inset-0 bg-black/40 z-40"
        onClick={onClose}
        aria-hidden
      />
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl shadow-xl max-h-[85vh] overflow-hidden flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="font-semibold text-lg">Atualizar valor</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-full hover:bg-gray-100"
            aria-label="Fechar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-y-auto p-4">
          {investment && (
            <p className="text-sm text-gray-500 mb-4">
              {investment.nome_produto} • {mesLabel}
            </p>
          )}

          {error && (
            <div className="rounded-lg bg-red-50 text-red-700 p-3 text-sm mb-4">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Valor total (R$)
              </label>
              <input
                type="text"
                inputMode="decimal"
                value={valorTotalInput}
                onChange={(e) => handleValorTotalChange(e.target.value)}
                placeholder="0"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 text-lg font-semibold focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quantidade
              </label>
              <input
                type="text"
                inputMode="decimal"
                value={quantidadeInput}
                onChange={(e) => handleQuantidadeChange(e.target.value)}
                placeholder="1"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Valor unitário (R$)
              </label>
              <input
                type="text"
                inputMode="decimal"
                value={valorUnitarioInput}
                onChange={(e) => setValorUnitarioInput(e.target.value)}
                placeholder="0,00"
                className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-3 rounded-xl border border-gray-300 font-medium text-gray-700"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 py-3 rounded-xl bg-indigo-600 text-white font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              Salvar
            </button>
          </div>
        </form>
      </div>
    </>
  )
}
