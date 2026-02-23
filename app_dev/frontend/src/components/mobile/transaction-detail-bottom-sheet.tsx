'use client'

/**
 * TransactionDetailBottomSheet
 *
 * Bottom sheet para detalhar e editar uma transação no mobile.
 * - Exibe dados da transação
 * - Permite editar grupo e subgrupo
 * - TipoGasto e CategoriaGeral são atualizados automaticamente pelo backend
 * - Se parcela: pergunta se quer atualizar em todas as parcelas
 * - Se base padrões: pergunta se quer atualizar em todas com o mesmo padrão
 */

import * as React from 'react'
import { X, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { CategoryIcon } from '@/components/mobile/category-icon'
import type { CategoryType } from '@/components/mobile/category-icon'

interface TransactionDetail {
  id: number
  IdTransacao: string
  Estabelecimento: string
  Valor: number
  Data: string
  GRUPO?: string
  SUBGRUPO?: string
  TipoGasto?: string
  CategoriaGeral?: string
  IdParcela?: string
  origem_classificacao?: string
  MesFatura?: string
  NomeCartao?: string
  banco_origem?: string
  TipoTransacao?: string
  tipodocumento?: string
}

interface PropagateInfo {
  same_parcela_count: number
  has_padrao: boolean
  same_padrao_count: number
}

interface TransactionDetailBottomSheetProps {
  isOpen: boolean
  onClose: () => void
  transaction: TransactionDetail | null
  onSaved: () => void
}

function grupoToCategory(grupo: string | undefined): CategoryType {
  if (!grupo) return 'outros'
  const g = grupo.toLowerCase()
  if (g.includes('casa') || g.includes('moradia') || g.includes('aluguel')) return 'casa'
  if (g.includes('aliment') || g.includes('restaurante')) return 'alimentacao'
  if (g.includes('compra') || g.includes('shopping')) return 'compras'
  if (g.includes('transporte') || g.includes('combust')) return 'transporte'
  if (g.includes('conta') || g.includes('utilidade')) return 'contas'
  if (g.includes('lazer') || g.includes('saúde') || g.includes('viagem')) return 'lazer'
  return 'outros'
}

export function TransactionDetailBottomSheet({
  isOpen,
  onClose,
  transaction,
  onSaved
}: TransactionDetailBottomSheetProps) {
  const [grupo, setGrupo] = React.useState('')
  const [subgrupo, setSubgrupo] = React.useState('')
  const [grupos, setGrupos] = React.useState<string[]>([])
  const [subgruposPorGrupo, setSubgruposPorGrupo] = React.useState<Record<string, string[]>>({})
  const [propagateInfo, setPropagateInfo] = React.useState<PropagateInfo | null>(null)
  const [propagateParcela, setPropagateParcela] = React.useState(false)
  const [propagatePadrao, setPropagatePadrao] = React.useState(false)
  const [loading, setLoading] = React.useState(false)
  const [saving, setSaving] = React.useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [deleting, setDeleting] = React.useState(false)

  const subgruposDisponiveis = React.useMemo(() => {
    if (!grupo) return []
    return subgruposPorGrupo[grupo] || []
  }, [grupo, subgruposPorGrupo])

  React.useEffect(() => {
    if (transaction) {
      setGrupo(transaction.GRUPO || '')
      setSubgrupo(transaction.SUBGRUPO || '')
      setPropagateParcela(false)
      setPropagatePadrao(false)
    }
  }, [transaction])

  React.useEffect(() => {
    if (isOpen) {
      fetchGrupos()
    }
  }, [isOpen])

  React.useEffect(() => {
    if (isOpen && transaction?.IdTransacao) {
      fetchPropagateInfo()
    }
  }, [isOpen, transaction?.IdTransacao])

  const fetchGrupos = async () => {
    try {
      const res = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/categories/grupos-subgrupos`
      )
      if (res.ok) {
        const data = await res.json()
        setGrupos(data.grupos || [])
        setSubgruposPorGrupo(data.subgruposPorGrupo || {})
      }
    } catch (e) {
      console.error('Erro ao buscar grupos:', e)
    }
  }

  const fetchPropagateInfo = async () => {
    if (!transaction?.IdTransacao) return
    setLoading(true)
    try {
      const res = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/propagate-info/${transaction.IdTransacao}`
      )
      if (res.ok) {
        const data = await res.json()
        setPropagateInfo(data)
      } else {
        setPropagateInfo(null)
      }
    } catch {
      setPropagateInfo(null)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!transaction) return

    setSaving(true)
    try {
      const body: Record<string, unknown> = {
        GRUPO: grupo || null,
        SUBGRUPO: subgrupo || null
      }
      if (hasIdParcela && propagateParcela) {
        body.propagate_parcela = true
      }
      if (propagateInfo?.has_padrao && propagateInfo.same_padrao_count > 0 && propagatePadrao) {
        body.propagate_padrao = true
      }

      const res = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/update/${transaction.IdTransacao}`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        }
      )

      if (res.ok) {
        onSaved()
        onClose()
      } else {
        const err = await res.json()
        toast.error(err.detail || 'Erro ao salvar')
      }
    } catch (e) {
      console.error('Erro ao salvar:', e)
      toast.error('Erro ao salvar. Tente novamente.')
    } finally {
      setSaving(false)
    }
  }

  const formatCurrency = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

  /** Mapeia TipoTransacao/tipodocumento para tipo_documento da API de exclusões */
  const getTipoDocumento = (): 'cartao' | 'extrato' | 'ambos' => {
    const t = (transaction?.tipodocumento || transaction?.TipoTransacao || '').toLowerCase()
    if (t.includes('cartão') || t.includes('cartao') || t === 'cartao') return 'cartao'
    if (t.includes('extrato')) return 'extrato'
    return 'ambos'
  }

  const handleDeleteClick = () => setDeleteDialogOpen(true)

  const handleConfirmDelete = async () => {
    if (!transaction) return

    setDeleting(true)
    try {
      const banco = transaction.banco_origem || null
      const tipoDocumento = getTipoDocumento()

      // 1. Adicionar à base de exclusões
      const exclusaoRes = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/exclusoes`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            nome_transacao: transaction.Estabelecimento.trim(),
            banco,
            tipo_documento: tipoDocumento,
            acao: 'EXCLUIR'
          })
        }
      )

      if (!exclusaoRes.ok) {
        const err = await exclusaoRes.json()
        throw new Error(err.detail || 'Erro ao adicionar à base de exclusões')
      }

      // 2. Deletar a transação
      const deleteRes = await fetchWithAuth(
        `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/transactions/${transaction.IdTransacao}`,
        { method: 'DELETE' }
      )

      if (!deleteRes.ok) {
        const err = await deleteRes.json()
        throw new Error(err.detail || 'Erro ao excluir transação')
      }

      onSaved()
      onClose()
      setDeleteDialogOpen(false)
    } catch (e) {
      console.error('Erro ao excluir:', e)
      toast.error(e instanceof Error ? e.message : 'Erro ao excluir. Tente novamente.')
    } finally {
      setDeleting(false)
    }
  }

  if (!isOpen) return null
  if (!transaction) return null

  const hasIdParcela = Boolean(transaction.IdParcela)
  const sameParcelaCount = propagateInfo?.same_parcela_count ?? 0
  const showPropagateParcela = hasIdParcela
  const showPropagatePadrao = Boolean(propagateInfo?.has_padrao && (propagateInfo?.same_padrao_count ?? 0) > 0)

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-[100] transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className={cn(
          'fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl z-[101]',
          'transform transition-transform duration-300 flex flex-col',
          'max-h-[85vh]'
        )}
      >
        <div className="flex justify-center pt-2 pb-1">
          <div className="w-12 h-1 bg-gray-300 rounded-full" />
        </div>

        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 shrink-0">
          <h2 className="text-base font-semibold text-gray-900">Detalhes da Transação</h2>
          <div className="flex items-center gap-1">
            <button
              onClick={handleDeleteClick}
              className="p-1.5 hover:bg-red-50 rounded-full text-gray-500 hover:text-red-600 transition-colors"
              aria-label="Excluir e adicionar à base de exclusões"
            >
              <Trash2 className="w-5 h-5" />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 hover:bg-gray-100 rounded-full"
              aria-label="Fechar"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4 min-h-0">
          {/* Resumo */}
          <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-xl mb-4">
            <CategoryIcon
              category={grupoToCategory(transaction.GRUPO)}
              size={48}
              iconSize={24}
            />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-gray-900 truncate">{transaction.Estabelecimento}</p>
              <p className="text-sm text-gray-500">
                {transaction.Data}
                {transaction.MesFatura && (
                  <span className="ml-2">
                    Fatura: {transaction.MesFatura.slice(4, 6)}/{transaction.MesFatura.slice(0, 4)}
                  </span>
                )}
              </p>
              <p
                className={cn(
                  'font-semibold mt-1',
                  transaction.Valor >= 0 ? 'text-green-600' : 'text-red-600'
                )}
              >
                {formatCurrency(transaction.Valor)}
              </p>
            </div>
          </div>

          {/* Grupo */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Grupo</label>
            <select
              value={grupo}
              onChange={(e) => {
                setGrupo(e.target.value)
                setSubgrupo('')
              }}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione</option>
              {grupos.map((g) => (
                <option key={g} value={g}>
                  {g}
                </option>
              ))}
            </select>
          </div>

          {/* Subgrupo */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Subgrupo</label>
            <select
              value={subgrupo}
              onChange={(e) => setSubgrupo(e.target.value)}
              disabled={!grupo}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <option value="">{grupo ? 'Selecione' : 'Selecione o grupo primeiro'}</option>
              {subgruposDisponiveis.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>

          {/* Propagação */}
          {(showPropagateParcela || showPropagatePadrao) && (
            <div className="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <p className="text-sm font-medium text-amber-800 mb-3">
                Deseja aplicar esta alteração em outras transações?
              </p>
              {showPropagateParcela && (
                <label className="flex items-center gap-2 mb-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={propagateParcela}
                    onChange={(e) => setPropagateParcela(e.target.checked)}
                    className="rounded border-gray-300 w-5 h-5"
                  />
                  <span className="text-sm text-gray-700">
                    {sameParcelaCount > 0
                      ? `Em todas as ${sameParcelaCount} parcelas desta compra`
                      : 'Em todas as parcelas desta compra'}
                  </span>
                </label>
              )}
              {showPropagatePadrao && (
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={propagatePadrao}
                    onChange={(e) => setPropagatePadrao(e.target.checked)}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm text-gray-700">
                    Em todas as {propagateInfo!.same_padrao_count} transações com este padrão
                  </span>
                </label>
              )}
            </div>
          )}

          <p className="text-xs text-gray-500">
            Tipo de Gasto e Categoria serão atualizados automaticamente conforme o grupo.
          </p>
        </div>

        {/* Footer fixo dentro do sheet - sempre visível */}
        <div className="shrink-0 flex gap-2.5 px-4 py-4 border-t border-gray-200 bg-white pb-[max(1rem,env(safe-area-inset-bottom))]">
          <button
            onClick={onClose}
            disabled={saving}
            className="flex-1 py-3 px-4 rounded-xl font-bold text-base bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-3 px-4 rounded-xl font-bold text-base bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </div>

      {/* Diálogo de confirmação: excluir e adicionar à base de exclusões */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir transação</AlertDialogTitle>
            <AlertDialogDescription>
              Deseja excluir esta transação e adicionar o nome &quot;{transaction?.Estabelecimento}&quot; na base de exclusões
              {transaction?.banco_origem ? ` para o banco ${transaction.banco_origem}` : ''}
              {getTipoDocumento() === 'cartao' ? ' e para fatura de cartão' : getTipoDocumento() === 'extrato' ? ' e para extrato' : ' e para fatura e extrato'}?
              {' '}Nas próximas importações, transações com esse nome serão automaticamente excluídas.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={(e) => {
                e.preventDefault()
                handleConfirmDelete()
              }}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? 'Excluindo...' : 'Sim, excluir e adicionar à base'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
