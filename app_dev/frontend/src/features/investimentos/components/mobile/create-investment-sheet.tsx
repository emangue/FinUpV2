'use client'

/**
 * Bottom sheet para criar novo investimento (mobile)
 */

import * as React from 'react'
import { X } from 'lucide-react'
import { createInvestimento } from '../../services/investimentos-api'
import type { CreateInvestimentoForm } from '../../types'

const TIPOS_COMUNS = [
  'Renda Fixa',
  'Fundo Imobiliário',
  'Ação',
  'Conta Corrente',
  'FGTS',
  'Previdência Privada',
  'Fundo de Investimento',
  'Apartamento',
  'Casa',
  'Automóvel',
]

interface CreateInvestmentSheetProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
  ano: number
  anomes: number
}

export function CreateInvestmentSheet({
  open,
  onClose,
  onSuccess,
  ano,
  anomes,
}: CreateInvestmentSheetProps) {
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  const [form, setForm] = React.useState({
    nome_produto: '',
    corretora: '',
    tipo_investimento: '',
    classe_ativo: 'Ativo',
    quantidade: 1,
    valor_unitario_inicial: '',
    percentual_cdi: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const valorUnit = parseFloat(form.valor_unitario_inicial.replace(',', '.')) || 0
    const qty = form.quantidade || 1
    const valorTotal = valorUnit * qty

    setLoading(true)
    setError(null)
    try {
      const balanceId = `mobile-${anomes}-${crypto.randomUUID().replace(/-/g, '').slice(0, 12)}`
      const data: CreateInvestimentoForm = {
        balance_id: balanceId,
        nome_produto: form.nome_produto.trim(),
        corretora: form.corretora.trim(),
        tipo_investimento: form.tipo_investimento,
        classe_ativo: form.classe_ativo,
        ano,
        anomes,
        quantidade: qty,
        valor_unitario_inicial: valorUnit,
        valor_total_inicial: valorTotal,
      }
      if (form.percentual_cdi) {
        data.percentual_cdi = parseFloat(form.percentual_cdi.replace(',', '.'))
      }
      await createInvestimento(data)
      onSuccess()
      onClose()
      setForm({ nome_produto: '', corretora: '', tipo_investimento: '', classe_ativo: 'Ativo', quantidade: 1, valor_unitario_inicial: '', percentual_cdi: '' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar')
    } finally {
      setLoading(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-end">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative w-full bg-white rounded-t-2xl max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-4 py-3 flex items-center justify-between">
          <h2 className="font-semibold text-gray-900">Novo investimento</h2>
          <button onClick={onClose} className="p-2 -mr-2">
            <X className="w-5 h-5" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <p className="text-red-600 text-sm">{error}</p>
          )}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nome</label>
            <input
              type="text"
              value={form.nome_produto}
              onChange={(e) => setForm((f) => ({ ...f, nome_produto: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Ex: Tesouro Selic 2029"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Corretora</label>
            <input
              type="text"
              value={form.corretora}
              onChange={(e) => setForm((f) => ({ ...f, corretora: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Ex: XP, Nubank"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tipo</label>
            <select
              value={form.tipo_investimento}
              onChange={(e) => setForm((f) => ({ ...f, tipo_investimento: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg"
              required
            >
              <option value="">Selecione</option>
              {TIPOS_COMUNS.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Classe</label>
            <select
              value={form.classe_ativo}
              onChange={(e) => setForm((f) => ({ ...f, classe_ativo: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="Ativo">Ativo</option>
              <option value="Passivo">Passivo</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Quantidade</label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={form.quantidade}
              onChange={(e) => setForm((f) => ({ ...f, quantidade: parseFloat(e.target.value) || 1 }))}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Valor unitário (R$)</label>
            <input
              type="text"
              inputMode="decimal"
              value={form.valor_unitario_inicial}
              onChange={(e) => setForm((f) => ({ ...f, valor_unitario_inicial: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="0,00"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">% CDI (opcional)</label>
            <input
              type="text"
              inputMode="decimal"
              value={form.percentual_cdi}
              onChange={(e) => setForm((f) => ({ ...f, percentual_cdi: e.target.value }))}
              className="w-full px-3 py-2 border rounded-lg"
              placeholder="Ex: 100"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 text-white rounded-xl font-semibold disabled:opacity-50"
          >
            {loading ? 'Salvando...' : 'Criar investimento'}
          </button>
        </form>
      </div>
    </div>
  )
}
