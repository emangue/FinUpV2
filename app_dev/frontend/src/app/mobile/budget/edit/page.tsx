'use client'

/**
 * Budget Edit Mobile - Edição de TODAS as metas do mês
 * 
 * Permite editar orçamento de múltiplas categorias de uma vez
 * Bulk update com PUT /budget/planning/bulk-upsert
 */

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { format } from 'date-fns'
import { Save, ArrowLeft } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { CategoryIcon } from '@/components/mobile/category-icon'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { cn } from '@/lib/utils'
import type { CategoryType } from '@/components/mobile/tracker-card'

interface CategoryBudgetEdit {
  grupo: string
  orcamento: number
  category: CategoryType
  categoryName: string
}

// Mapear grupos do backend para categorias do frontend
const GROUP_TO_CATEGORY: Record<string, { category: CategoryType; name: string }> = {
  'Casa': { category: 'casa', name: 'Casa' },
  'Alimentação': { category: 'alimentacao', name: 'Alimentação' },
  'Compras': { category: 'compras', name: 'Compras' },
  'Transporte': { category: 'transporte', name: 'Transporte' },
  'Contas': { category: 'contas', name: 'Contas' },
  'Lazer': { category: 'lazer', name: 'Lazer' },
}

function BudgetEditContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const mesReferencia = searchParams.get('mes_referencia') || format(new Date(), 'yyyy-MM')
  
  const [budgets, setBudgets] = React.useState<CategoryBudgetEdit[]>([])
  const [loading, setLoading] = React.useState(true)
  const [saving, setSaving] = React.useState(false)
  
  React.useEffect(() => {
    fetchBudgets()
  }, [mesReferencia])
  
  const fetchBudgets = async () => {
    try {
      setLoading(true)
      
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      const response = await fetchWithAuth(
        `${BASE_URL}/budget/planning?mes_referencia=${mesReferencia}`
      )
      
      if (response.status === 401) {
        router.push('/login')
        return
      }
      
      if (!response.ok) {
        console.error('Erro ao buscar orçamentos:', response.status, response.statusText)
        throw new Error(`Erro ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Dados recebidos:', data)
      
      // A API pode retornar data.planning ou data.items
      const planningData = data.planning || data.items || []
      
      // Mapear para formato editável
      const mapped: CategoryBudgetEdit[] = planningData
        .map((item: any) => {
          const mapping = GROUP_TO_CATEGORY[item.Grupo || item.grupo]
          if (!mapping) return null
          
          return {
            grupo: item.Grupo || item.grupo,
            orcamento: item.Orcamento || item.orcamento || 0,
            category: mapping.category,
            categoryName: mapping.name
          }
        })
        .filter(Boolean)
      
      setBudgets(mapped)
    } catch (error) {
      console.error('Erro ao buscar orçamentos:', error)
      alert('Erro ao carregar metas')
    } finally {
      setLoading(false)
    }
  }
  
  const handleValueChange = (grupo: string, value: string) => {
    const numericValue = parseFloat(value) || 0
    
    setBudgets(prev => prev.map(b => 
      b.grupo === grupo 
        ? { ...b, orcamento: numericValue }
        : b
    ))
  }
  
  const handleSave = async () => {
    try {
      setSaving(true)
      
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      
      // Bulk upsert
      const payload = budgets.map(b => ({
        grupo: b.grupo,
        valor_planejado: b.orcamento
      }))
      
      const response = await fetchWithAuth(
        `${BASE_URL}/budget/planning/bulk-upsert`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            mes_referencia: mesReferencia,
            items: payload
          })
        }
      )
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}`)
      }
      
      // Voltar para página de metas
      router.back()
    } catch (error) {
      console.error('Erro ao salvar metas:', error)
      alert('Erro ao salvar metas. Tente novamente.')
    } finally {
      setSaving(false)
    }
  }
  
  // Formatar mes_referencia para exibição (YYYY-MM → MM/YYYY)
  const formatMesReferencia = (mesRef: string) => {
    const [year, month] = mesRef.split('-')
    return `${month}/${year}`
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title={`Editar Metas - ${formatMesReferencia(mesReferencia)}`}
        leftAction="back"
        onBack={() => router.back()}
        rightActions={[
          {
            icon: <Save className="w-5 h-5" />,
            label: 'Salvar',
            onClick: () => { if (!saving && !loading) handleSave(); },
          },
        ]}
      />
      
      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-500">Carregando...</div>
          </div>
        ) : (
          <div className="space-y-4">
            {budgets.map((budget) => (
              <div
                key={budget.grupo}
                className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100"
              >
                <div className="flex items-center gap-3 mb-3">
                  <CategoryIcon category={budget.category} size={40} />
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">
                      {budget.categoryName}
                    </div>
                    <p className="text-xs text-gray-600">Meta mensal</p>
                  </div>
                </div>
                
                <div className="relative">
                  <label htmlFor={`budget-${budget.grupo}`} className="sr-only">
                    Meta mensal para {budget.categoryName}
                  </label>
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 font-medium" aria-hidden="true">
                    R$
                  </span>
                  <input
                    id={`budget-${budget.grupo}`}
                    type="number"
                    inputMode="decimal"
                    value={budget.orcamento}
                    onChange={(e) => handleValueChange(budget.grupo, e.target.value)}
                    aria-label={`Meta mensal para ${budget.categoryName}`}
                    className={cn(
                      'w-full pl-10 pr-4 py-3 text-lg font-semibold',
                      'border-2 border-gray-200 rounded-xl',
                      'focus:outline-none focus:border-blue-500',
                      'transition-colors'
                    )}
                    placeholder="0,00"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Sticky Bottom Button */}
      {!loading && (
        <div className="p-5 bg-white border-t border-gray-200">
          <button
            onClick={handleSave}
            disabled={saving}
            className={cn(
              'w-full py-4 rounded-xl font-semibold text-lg',
              'transition-all',
              saving
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]'
            )}
          >
            {saving ? 'Salvando...' : 'Salvar Todas as Metas'}
          </button>
        </div>
      )}
    </div>
  )
}

export default function BudgetEditPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col h-screen bg-gray-50 items-center justify-center">
        <div className="text-gray-500">Carregando...</div>
      </div>
    }>
      <BudgetEditContent />
    </Suspense>
  )
}
