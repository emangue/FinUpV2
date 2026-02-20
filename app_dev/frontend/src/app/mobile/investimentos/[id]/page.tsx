'use client'

/**
 * Detalhe do investimento - Mobile
 */

import * as React from 'react'
import { useRouter, useParams, useSearchParams } from 'next/navigation'
import { ArrowLeft, Pencil, Trash2 } from 'lucide-react'
import { getInvestimento, deleteHistoricoMes } from '@/features/investimentos/services/investimentos-api'
import type { InvestimentoPortfolio } from '@/features/investimentos/types'
import { EditInvestmentModal } from '@/features/investimentos/components/edit-investment-modal'
import { useRequireAuth } from '@/core/hooks/use-require-auth'

export default function InvestimentoDetailMobilePage() {
  const router = useRouter()
  const params = useParams()
  const searchParams = useSearchParams()
  const isAuth = useRequireAuth()
  const id = Number(params.id)
  const anomesParam = searchParams.get('anomes')
  const anomes = anomesParam ? parseInt(anomesParam, 10) : undefined

  const [investment, setInvestment] = React.useState<InvestimentoPortfolio | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [editOpen, setEditOpen] = React.useState(false)
  const [deleting, setDeleting] = React.useState(false)

  const loadInvestment = React.useCallback(() => {
    if (!isAuth || !id) return
    getInvestimento(id, anomes)
      .then(setInvestment)
      .catch((err) => setError(err?.message || 'Erro ao carregar'))
      .finally(() => setLoading(false))
  }, [isAuth, id, anomes])

  React.useEffect(() => {
    setLoading(true)
    loadInvestment()
  }, [loadInvestment])

  const valorTotal = investment?.valor_total_mes != null
    ? (typeof investment.valor_total_mes === 'number' ? investment.valor_total_mes : parseFloat(String(investment.valor_total_mes)) || 0)
    : parseFloat(investment?.valor_total_inicial || '0') || 0
  let valorUnitario = investment?.valor_unitario_mes != null
    ? (typeof investment.valor_unitario_mes === 'number' ? investment.valor_unitario_mes : parseFloat(String(investment.valor_unitario_mes)) || 0)
    : parseFloat(investment?.valor_unitario_inicial || '0') || 0
  const quantidade = investment?.quantidade_mes ?? investment?.quantidade ?? 1
  if (valorTotal !== 0 && (valorUnitario === 0 || !valorUnitario)) {
    valorUnitario = valorTotal / (quantidade || 1)
  }

  const formatCurrency = (v: string | number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0 }).format(
      typeof v === 'string' ? parseFloat(v) : v
    )
  const formatDate = (s: string | undefined) =>
    s ? new Date(s).toLocaleDateString('pt-BR') : '-'

  if (!isAuth) return null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-20 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3">
        <button
          onClick={() => router.push('/mobile/investimentos')}
          className="p-2 -ml-2 rounded-full hover:bg-gray-100"
          aria-label="Voltar"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="font-semibold text-gray-900 truncate flex-1">
          {investment?.nome_produto || 'Detalhe'}
        </h1>
        {investment && (
          <div className="flex items-center gap-1">
            {anomes && (
              <button
                onClick={async () => {
                  if (!confirm('Remover este investimento deste mês?')) return
                  setDeleting(true)
                  try {
                    await deleteHistoricoMes(id, anomes)
                    router.push(`/mobile/investimentos?anomes=${anomes}`)
                  } catch (err) {
                    alert(err instanceof Error ? err.message : 'Erro ao remover')
                  } finally {
                    setDeleting(false)
                  }
                }}
                disabled={deleting}
                className="p-2 rounded-full hover:bg-red-50 text-gray-500 hover:text-red-600 disabled:opacity-50"
                aria-label="Remover deste mês"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={() => setEditOpen(true)}
              className="p-2 rounded-full hover:bg-gray-100"
              aria-label="Editar valor e detalhes"
            >
              <Pencil className="w-5 h-5" />
            </button>
          </div>
        )}
      </header>

      <div className="p-5">
        {loading ? (
          <div className="flex justify-center py-16">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
          </div>
        ) : error ? (
          <p className="text-red-600 text-center py-8">{error}</p>
        ) : investment ? (
          <div className="space-y-6">
            <div className="bg-white rounded-xl p-5 border border-gray-200">
              <h2 className="text-sm font-medium text-gray-500 mb-1">Tipo</h2>
              <p className="font-semibold text-gray-900">{investment.tipo_investimento}</p>
            </div>

            <div className="bg-white rounded-xl p-5 border border-gray-200 space-y-4">
              <h2 className="text-sm font-semibold text-gray-900">Valores</h2>
              <div>
                <p className="text-xs text-gray-500">Quantidade</p>
                <p className="font-bold text-lg">{quantidade}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Valor unitário</p>
                <p className="font-bold text-lg">{formatCurrency(valorUnitario)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Valor total</p>
                <p className="font-bold text-lg text-indigo-600">{formatCurrency(valorTotal)}</p>
              </div>
              {investment.percentual_cdi != null && investment.percentual_cdi > 0 && (
                <div>
                  <p className="text-xs text-gray-500">% CDI</p>
                  <p className="font-bold text-lg">{investment.percentual_cdi}%</p>
                </div>
              )}
            </div>

            <div className="bg-white rounded-xl p-5 border border-gray-200 space-y-4">
              <h2 className="text-sm font-semibold text-gray-900">Datas</h2>
              <div>
                <p className="text-xs text-gray-500">Data de aplicação</p>
                <p className="font-medium">{formatDate(investment.data_aplicacao)}</p>
              </div>
              {investment.data_vencimento && (
                <div>
                  <p className="text-xs text-gray-500">Data de vencimento</p>
                  <p className="font-medium">{formatDate(investment.data_vencimento)}</p>
                </div>
              )}
            </div>

            {investment.corretora && (
              <div className="bg-white rounded-xl p-5 border border-gray-200">
                <p className="text-xs text-gray-500">Corretora</p>
                <p className="font-medium">{investment.corretora}</p>
              </div>
            )}
          </div>
        ) : null}
      </div>

      <EditInvestmentModal
        investment={investment}
        open={editOpen}
        onClose={() => setEditOpen(false)}
        onSuccess={loadInvestment}
        anomes={anomes}
      />
    </div>
  )
}
