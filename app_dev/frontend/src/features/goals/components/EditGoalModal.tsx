'use client'

/**
 * EditGoalModal Component
 * Modal para editar meta existente
 * 
 * Features:
 * - Form com nome, descrição, orçamento
 * - Validação de campos
 * - Integração com API bulk-upsert
 * - Opção de aplicar para meses futuros
 * - Botão de excluir meta
 */

import * as React from 'react'
import { X } from 'lucide-react'
import { Goal } from '../types'
import { GOAL_COLORS } from '../lib/colors'

interface EditGoalModalProps {
  goal: Goal
  isOpen: boolean
  onClose: () => void
  onSave: (data: EditGoalData) => Promise<void>
  onDelete: () => Promise<void>
}

export interface EditGoalData {
  nome: string
  descricao: string
  orcamento: number
  cor?: string
  aplicarMesesFuturos: boolean
}

export function EditGoalModal({ goal, isOpen, onClose, onSave, onDelete }: EditGoalModalProps) {
  const [nome, setNome] = React.useState(goal.grupo)
  const [descricao, setDescricao] = React.useState('')
  const [orcamento, setOrcamento] = React.useState(goal.valor_planejado.toString())
  const [cor, setCor] = React.useState(goal.cor || '')
  const [aplicarFuturos, setAplicarFuturos] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(false)
  const [isDeleting, setIsDeleting] = React.useState(false)

  // Reset form when goal changes
  React.useEffect(() => {
    setNome(goal.grupo)
    setDescricao('')
    setOrcamento(goal.valor_planejado.toString())
    setCor(goal.cor || '')
    setAplicarFuturos(false)
  }, [goal])

  const handleSave = async () => {
    if (!nome.trim()) {
      alert('Nome é obrigatório')
      return
    }

    const orcamentoNum = parseFloat(orcamento)
    if (isNaN(orcamentoNum) || orcamentoNum <= 0) {
      alert('Orçamento deve ser maior que zero')
      return
    }

    setIsLoading(true)
    try {
      await onSave({
        nome: nome.trim(),
        descricao: descricao.trim(),
        orcamento: orcamentoNum,
        cor: cor || undefined,
        aplicarMesesFuturos: aplicarFuturos
      })
      onClose()
    } catch (error) {
      console.error('Erro ao salvar meta:', error)
      alert('Erro ao salvar meta. Tente novamente.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    const confirmacao = confirm(
      `Deseja realmente excluir a meta "${nome}"?\n\nEsta ação não pode ser desfeita.`
    )
    
    if (!confirmacao) return

    setIsDeleting(true)
    try {
      await onDelete()
      onClose()
    } catch (error) {
      console.error('Erro ao excluir meta:', error)
      alert('Erro ao excluir meta. Tente novamente.')
    } finally {
      setIsDeleting(false)
    }
  }

  const handleOrcamentoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    // Permite apenas números e ponto decimal
    if (value === '' || /^\d*\.?\d*$/.test(value)) {
      setOrcamento(value)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-end sm:items-center justify-center p-0 sm:p-4">
      <div 
        className="bg-white w-full sm:max-w-lg rounded-t-3xl sm:rounded-3xl max-h-[90vh] overflow-y-auto animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <header className="sticky top-0 bg-white rounded-t-3xl px-6 py-4 flex items-center justify-between border-b border-gray-100 z-10">
          <button 
            onClick={onClose}
            disabled={isLoading || isDeleting}
            className="text-gray-700 hover:text-gray-900 transition-colors disabled:opacity-50"
          >
            <X className="w-6 h-6" />
          </button>
          <h1 className="text-lg font-bold text-gray-800">Editar Meta</h1>
          <button 
            onClick={handleSave}
            disabled={isLoading || isDeleting}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Salvando...' : 'Salvar'}
          </button>
        </header>

        {/* Date */}
        <div className="bg-white px-6 py-2">
          <p className="text-xs text-gray-400 text-right">{goal.mes_referencia}</p>
        </div>

        {/* Main Content */}
        <div className="bg-white px-6 pb-6">
          <div className="pt-4 space-y-5">
            {/* Nome */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-2">
                Nome da Meta *
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                disabled={isLoading || isDeleting}
                placeholder="Ex: Alimentação, Casa, Carro"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            {/* Descrição */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-2">
                Descrição (opcional)
              </label>
              <input
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                disabled={isLoading || isDeleting}
                placeholder="Ex: Gastos com supermercado e restaurantes"
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              />
            </div>

            {/* Cor no gráfico donut */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-2">
                Cor no gráfico
              </label>
              <div className="flex flex-wrap gap-2">
                {GOAL_COLORS.map((c) => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => setCor(cor === c ? '' : c)}
                    className={`w-8 h-8 rounded-full border-2 transition-all ${
                      cor === c ? 'border-gray-900 scale-110' : 'border-transparent hover:scale-105'
                    }`}
                    style={{ backgroundColor: c }}
                    aria-label={`Cor ${c}`}
                  />
                ))}
              </div>
              {cor && (
                <button
                  type="button"
                  onClick={() => setCor('')}
                  className="text-xs text-gray-500 mt-2 hover:text-gray-700"
                >
                  Remover cor personalizada
                </button>
              )}
            </div>

            {/* Orçamento */}
            <div>
              <label className="block text-xs font-semibold text-gray-700 mb-2">
                Orçamento Mensal *
              </label>
              <div className="relative">
                <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 font-semibold">
                  R$
                </span>
                <input
                  type="text"
                  inputMode="decimal"
                  value={orcamento}
                  onChange={handleOrcamentoChange}
                  disabled={isLoading || isDeleting}
                  placeholder="0.00"
                  className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                />
              </div>
              {/* REMOVIDO: Valor atual (total_mensal não existe mais) */}
            </div>

            {/* Info sobre progresso */}
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-start gap-3">
                <div className="text-blue-600 mt-0.5">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold text-gray-900">Sobre o orçamento</div>
                  <div className="text-xs text-gray-600 mt-1">
                    O valor planejado será comparado com suas transações reais do mês 
                    para calcular o percentual de uso do orçamento.
                  </div>
                </div>
              </div>
            </div>

            {/* Aplicar para Meses Futuros */}
            <div className="pt-2">
              <div className="border-t border-gray-200 pt-4">
                <label className="block text-xs font-semibold text-gray-700 mb-3">Recorrência</label>
                <label className="flex items-center justify-between p-4 bg-blue-50 border-2 border-blue-200 rounded-xl cursor-pointer hover:bg-blue-100 transition-colors">
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-gray-900">
                      Aplicar para meses posteriores
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      As alterações serão aplicadas para todos os meses seguintes
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    checked={aplicarFuturos}
                    onChange={(e) => setAplicarFuturos(e.target.checked)}
                    disabled={isLoading || isDeleting}
                    className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                  />
                </label>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Actions */}
        <div className="sticky bottom-0 bg-white border-t border-gray-100 px-6 py-4 space-y-3">
          <button
            onClick={handleSave}
            disabled={isLoading || isDeleting}
            className="w-full bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl py-4 font-bold shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Salvando...' : 'Salvar Alterações'}
          </button>
          <button
            onClick={handleDelete}
            disabled={isLoading || isDeleting}
            className="w-full bg-white text-red-600 border-2 border-red-200 rounded-2xl py-4 font-bold hover:bg-red-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isDeleting ? 'Excluindo...' : 'Excluir Meta'}
          </button>
        </div>
      </div>
    </div>
  )
}
