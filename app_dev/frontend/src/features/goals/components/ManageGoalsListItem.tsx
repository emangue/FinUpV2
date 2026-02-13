'use client'

import { Goal } from '../types'
import { useState, useEffect, useRef } from 'react'
import { debounce } from 'lodash'

interface ManageGoalsListItemProps {
  goal: Goal
  isActive: boolean
  onToggle: (goalId: string, currentState: boolean) => void
  onEdit: (goalId: string) => void
  onUpdateValor: (goalId: string, novoValor: number, aplicarAteFinAno: boolean) => Promise<void>
}

export function ManageGoalsListItem({
  goal,
  isActive,
  onToggle,
  onEdit,
  onUpdateValor,
}: ManageGoalsListItemProps) {
  const iconMap: Record<string, string> = {
    casa: '🏠',
    mercado: '🛒',
    transporte: '🚗',
    saude: '🏥',
    lazer: '🎉',
    educacao: '📚',
    investimento: '💰',
  }

  const icon = iconMap[goal.grupo?.toLowerCase() || 'investimento'] || '💼'
  
  const [valor, setValor] = useState(goal.valor_planejado.toString())
  const [isSaving, setIsSaving] = useState(false)
  const [valorMudou, setValorMudou] = useState(false)
  const [aplicarAteFinAno, setAplicarAteFinAno] = useState(true) // Default: true
  const inputRef = useRef<HTMLInputElement>(null)
  
  // Debounced save - salva 1200ms depois que parar de digitar (mais tempo para marcar checkbox)
  const debouncedSave = useRef(
    debounce(async (goalId: string, novoValor: number, aplicarAno: boolean) => {
      setIsSaving(true)
      try {
        await onUpdateValor(goalId, novoValor, aplicarAno)
        setValorMudou(false) // Esconde checkbox após salvar
      } catch (error) {
        console.error('Erro ao salvar:', error)
      } finally {
        setIsSaving(false)
      }
    }, 1200)
  ).current
  
  useEffect(() => {
    return () => {
      debouncedSave.cancel()
    }
  }, [debouncedSave])
  
  const handleValorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value.replace(/[^\d]/g, '') // Remove tudo exceto dígitos
    setValor(newValue)
    
    const numericValue = parseFloat(newValue) || 0
    if (numericValue !== goal.valor_planejado) {
      setValorMudou(true) // Mostra checkbox
      debouncedSave(goal.id.toString(), numericValue, aplicarAteFinAno)
    } else {
      setValorMudou(false) // Esconde se voltou ao valor original
    }
  }
  
  const handleFocus = () => {
    inputRef.current?.select()
  }
  
  // Calcular porcentagem usando valor_medio_3_meses em relação à meta
  const valorMedio = goal.valor_medio_3_meses || 0
  const metaAtual = parseFloat(valor) || goal.valor_planejado
  const percentualMedia = metaAtual > 0 ? Math.min((valorMedio / metaAtual) * 100, 100) : 0
  
  // Cores baseadas na relação média/meta
  const getBarColor = () => {
    if (percentualMedia >= 90) return 'bg-red-500'     // Média muito próxima/acima da meta (alerta)
    if (percentualMedia >= 70) return 'bg-yellow-500'  // Média alta (atenção)
    if (percentualMedia >= 40) return 'bg-green-500'   // Média moderada (ok)
    return 'bg-blue-500'                                // Média baixa (sobra)
  }

  return (
    <div
      className="p-4 bg-gray-50 rounded-2xl border-2 border-transparent hover:border-blue-200 transition-all"
      style={{ opacity: isActive ? 1 : 0.5 }}
    >
      <div className="flex items-center gap-3 mb-3">
        {/* Drag Handle (visual only - not functional yet) */}
        <button className="text-gray-400 hover:text-gray-600 cursor-grab active:cursor-grabbing">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 8h16M4 16h16"
            />
          </svg>
        </button>

        {/* Icon */}
        <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-xl">
          {icon}
        </div>

        {/* Goal Info */}
        <div className="flex-1 min-w-0">
          <h3 className="text-sm font-bold text-gray-900">{goal.grupo}</h3>
          
          {/* Input Editável para Valor */}
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-500">R$</span>
            <input
              ref={inputRef}
              type="text"
              value={(parseFloat(valor) || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              onChange={handleValorChange}
              onFocus={handleFocus}
              className="w-24 px-1.5 py-0.5 text-xs font-medium bg-white border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-transparent"
            />
            <span className="text-xs text-gray-500">/mês</span>
            {isSaving && (
              <span className="text-xs text-blue-500 animate-pulse">salvando...</span>
            )}
          </div>
        </div>

        {/* Toggle Active */}
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={isActive}
            onChange={() => onToggle(goal.id.toString(), isActive)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
        </label>

        {/* Edit Button */}
        <button
          onClick={() => onEdit(goal.id.toString())}
          className="text-gray-400 hover:text-blue-600 transition-colors"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>
      </div>
      
      {/* Checkbox: Aplicar até final do ano - Aparece quando valor muda */}
      {valorMudou && (
        <div className="ml-16 mb-2 p-2 bg-blue-50 border border-blue-200 rounded-lg">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={aplicarAteFinAno}
              onChange={(e) => {
                setAplicarAteFinAno(e.target.checked)
                // Reprocessa com nova opção
                const numericValue = parseFloat(valor) || goal.valor_planejado
                debouncedSave.cancel() // Cancela timer anterior
                debouncedSave(goal.id.toString(), numericValue, e.target.checked)
              }}
              className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
            />
            <span className="text-xs text-gray-700">
              Aplicar para todos os meses seguintes até {new Date().getFullYear()}
            </span>
          </label>
        </div>
      )}
      
      {/* Seção Total Mensal + Barra Visual */}
      <div className="ml-16 space-y-1.5">
        {/* Total do mês atual */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">Total mensal:</span>
          <span className="font-medium text-gray-700">
            R$ {totalMensal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </span>
        </div>
        
        {/* Barra Visual: Média vs Meta */}
        <div className="relative h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div 
            className={`absolute left-0 top-0 h-full ${getBarColor()} transition-all duration-300 rounded-full`}
            style={{ width: `${percentualMedia}%` }}
          />
        </div>
        
        {/* Legenda da Barra */}
        <div className="flex justify-between text-xs text-gray-400">
          <span>R$ 0</span>
          <span className="font-medium">
            {percentualMedia.toFixed(0)}% da meta
          </span>
        </div>
      </div>
    </div>
  )
}
