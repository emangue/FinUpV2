'use client'

/**
 * BudgetEditBottomSheet
 * 
 * Bottom sheet para edição rápida de uma meta específica
 * Aparece ao clicar em um TrackerCard
 * 
 * Features:
 * - Input numérico com teclado nativo
 * - Formatação em tempo real (R$)
 * - Salvar com PUT /budget/planning/:id
 */

import * as React from 'react'
import { X } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import { CategoryIcon } from '@/components/mobile/category-icon'
import type { CategoryType } from '@/components/mobile/tracker-card'

interface BudgetEditBottomSheetProps {
  isOpen: boolean
  onClose: () => void
  category: CategoryType
  categoryName: string
  currentBudget: number
  onSave: (newBudget: number) => Promise<void>
}

export function BudgetEditBottomSheet({
  isOpen,
  onClose,
  category,
  categoryName,
  currentBudget,
  onSave
}: BudgetEditBottomSheetProps) {
  const [value, setValue] = React.useState(currentBudget.toString())
  const [saving, setSaving] = React.useState(false)
  const inputRef = React.useRef<HTMLInputElement>(null)
  
  // Atualizar valor quando props mudarem
  React.useEffect(() => {
    setValue(currentBudget.toString())
  }, [currentBudget])
  
  // Focus no input quando abrir
  React.useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus()
      }, 100)
    }
  }, [isOpen])
  
  const handleSave = async () => {
    const numericValue = parseFloat(value)
    
    if (isNaN(numericValue) || numericValue < 0) {
      toast.error('Por favor, insira um valor válido')
      return
    }
    
    try {
      setSaving(true)
      await onSave(numericValue)
      onClose()
    } catch (error) {
      console.error('Erro ao salvar meta:', error)
      toast.error('Erro ao salvar meta. Tente novamente.')
    } finally {
      setSaving(false)
    }
  }
  
  const formatCurrency = (val: string) => {
    // Remove tudo exceto números e vírgula/ponto
    const cleaned = val.replace(/[^\d.,]/g, '').replace(',', '.')
    return cleaned
  }
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(formatCurrency(e.target.value))
  }
  
  if (!isOpen) return null
  
  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* Bottom Sheet */}
      <div
        className={cn(
          'fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl z-50',
          'transform transition-transform duration-300',
          'flex flex-col',
          isOpen ? 'translate-y-0' : 'translate-y-full'
        )}
        style={{ height: '55vh' }}
      >
        {/* Handle */}
        <div className="flex justify-center pt-2 pb-1">
          <div className="w-12 h-1 bg-gray-300 rounded-full" />
        </div>
        
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <CategoryIcon category={category} size={36} />
            <div>
              <h1 className="text-base font-semibold text-gray-900">
                Editar Meta
              </h1>
              <p className="text-xs text-gray-600">{categoryName}</p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-y-auto px-4 py-4" style={{ paddingBottom: '100px' }}>
          {/* Input */}
          <div>
            <label htmlFor="budget-value-input" className="block text-sm font-medium text-gray-700 mb-2">
              Valor do Orçamento
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-base font-medium" aria-hidden="true">
                R$
              </span>
              <input
                id="budget-value-input"
                ref={inputRef}
                type="number"
                inputMode="decimal"
                value={value}
                onChange={handleChange}
                aria-describedby="budget-hint"
                className={cn(
                  'w-full pl-10 pr-4 py-3 text-xl font-bold',
                  'border-2 border-gray-200 rounded-xl',
                  'focus:outline-none focus:border-blue-500',
                  'transition-colors'
                )}
                placeholder="0,00"
              />
            </div>
            <p id="budget-hint" className="text-xs text-gray-600 mt-1.5">
              Meta mensal para {categoryName}
            </p>
          </div>
        </div>
        
        {/* Actions - FIXO NO BOTTOM */}
        <div className="fixed bottom-0 left-0 right-0 flex gap-2.5 px-4 py-4 border-t border-gray-200 bg-white z-10">
          <button
            onClick={onClose}
            disabled={saving}
            className={cn(
              'flex-1 py-3 px-4 rounded-xl font-bold text-base',
              'bg-gray-100 text-gray-700',
              'hover:bg-gray-200 active:scale-95 transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            Cancelar
          </button>
          
          <button
            onClick={handleSave}
            disabled={saving}
            className={cn(
              'flex-1 py-3 px-4 rounded-xl font-bold text-base',
              'bg-blue-600 text-white',
              'hover:bg-blue-700 active:scale-95 transition-all',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            {saving ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
        
        {/* Safe area for iOS */}
        <div className="h-[env(safe-area-inset-bottom)]" />
      </div>
    </>
  )
}
