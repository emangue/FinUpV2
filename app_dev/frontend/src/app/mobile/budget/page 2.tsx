'use client'

/**
 * Budget Mobile - Tela de Metas (Trackers)
 * 
 * Integra:
 * - MonthScrollPicker (scroll de meses)
 * - YTDToggle (toggle mês/ano)
 * - TrackerCard (cards de categoria)
 * - MobileHeader (header unificado)
 * - BudgetEditBottomSheet (edição rápida)
 * 
 * Baseado no design "Trackers" do Style Guide
 * 
 * Endpoints usados:
 * - GET /api/v1/budget/planning?ano_mes=YYYYMM
 * - GET /api/v1/transactions/grupo-breakdown?data_inicio=X&data_fim=Y
 */

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { startOfMonth, endOfMonth, startOfYear, format } from 'date-fns'
import { Edit3 } from 'lucide-react'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { YTDToggle, YTDToggleValue } from '@/components/mobile/ytd-toggle'
import { TrackerCard, type CategoryType } from '@/components/mobile/tracker-card'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { BudgetEditBottomSheet } from '@/components/mobile/budget-edit-bottom-sheet'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'

interface CategoryBudget {
  grupo: string
  orcamento: number
  gasto: number
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

export default function BudgetMobilePage() {
  const router = useRouter()
  const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
  const [period, setPeriod] = React.useState<YTDToggleValue>('month')
  const [budgets, setBudgets] = React.useState<CategoryBudget[]>([])
  const [loading, setLoading] = React.useState(true)
  
  // Estado para bottom sheet de edição
  const [editingBudget, setEditingBudget] = React.useState<CategoryBudget | null>(null)
  const [isEditSheetOpen, setIsEditSheetOpen] = React.useState(false)
  
  // Buscar orçamentos quando mês ou período mudar
  React.useEffect(() => {
    fetchBudgets()
  }, [selectedMonth, period])
  
  const fetchBudgets = async () => {
    try {
      setLoading(true)
      
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      
      // Calcular datas baseado no período
      let startDate: Date
      let endDate: Date
      
      if (period === 'month') {
        startDate = startOfMonth(selectedMonth)
        endDate = endOfMonth(selectedMonth)
      } else {
        // Year-to-Date
        startDate = startOfYear(selectedMonth)
        endDate = endOfMonth(selectedMonth)
      }
      
      const startDateStr = format(startDate, 'yyyy-MM-dd')
      const endDateStr = format(endDate, 'yyyy-MM-dd')
      
      // Buscar gastos por grupo
      const breakdownResponse = await fetchWithAuth(
        `${BASE_URL}/transactions/grupo-breakdown?data_inicio=${startDateStr}&data_fim=${endDateStr}`
      )
      
      if (breakdownResponse.status === 401) {
        console.error('Não autenticado. Redirecionando para login...')
        router.push('/login')
        return
      }
      
      if (!breakdownResponse.ok) {
        throw new Error(`Erro ${breakdownResponse.status}: ${breakdownResponse.statusText}`)
      }
      
      const breakdownData = await breakdownResponse.json()
      
      // Buscar orçamentos planejados (usar mês selecionado)
      const mesReferencia = format(selectedMonth, 'yyyy-MM')
      const planningResponse = await fetchWithAuth(
        `${BASE_URL}/budget/planning?mes_referencia=${mesReferencia}`
      )
      
      let planningData: any[] = []
      if (planningResponse.ok) {
        const data = await planningResponse.json()
        planningData = data.planning || []
      }
      
      // Consolidar dados
      const budgetMap = new Map<string, CategoryBudget>()
      
      // Adicionar orçamentos planejados
      planningData.forEach((item: any) => {
        if (item.Grupo && GROUP_TO_CATEGORY[item.Grupo]) {
          budgetMap.set(item.Grupo, {
            grupo: item.Grupo,
            orcamento: item.Orcamento || 0,
            gasto: 0,
          })
        }
      })
      
      // Adicionar gastos reais
      if (breakdownData.grupos) {
        Object.entries(breakdownData.grupos).forEach(([grupo, data]: [string, any]) => {
          if (GROUP_TO_CATEGORY[grupo]) {
            const existing = budgetMap.get(grupo)
            if (existing) {
              existing.gasto = Math.abs(data.total || 0)
            } else {
              budgetMap.set(grupo, {
                grupo,
                orcamento: 0,
                gasto: Math.abs(data.total || 0),
              })
            }
          }
        })
      }
      
      // Converter para array e ordenar
      const budgetArray = Array.from(budgetMap.values())
        .filter(b => b.orcamento > 0 || b.gasto > 0)
        .sort((a, b) => a.grupo.localeCompare(b.grupo))
      
      setBudgets(budgetArray)
      
    } catch (error) {
      console.error('Erro ao buscar orçamentos:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleEditClick = (budget: CategoryBudget) => {
    setEditingBudget(budget)
    setIsEditSheetOpen(true)
  }
  
  const handleSaveBudget = async (newBudget: number) => {
    if (!editingBudget) return
    
    const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
    const mesReferencia = format(selectedMonth, 'yyyy-MM')
    
    const response = await fetchWithAuth(
      `${BASE_URL}/budget/planning/bulk-upsert`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mes_referencia: mesReferencia,
          items: [{
            grupo: editingBudget.grupo,
            valor_planejado: newBudget
          }]
        })
      }
    )
    
    if (!response.ok) {
      throw new Error(`Erro ${response.status}`)
    }
    
    // Recarregar dados
    await fetchBudgets()
  }
  
  const handleEditAll = () => {
    const mesReferencia = format(selectedMonth, 'yyyy-MM')
    router.push(`/mobile/budget/edit?mes_referencia=${mesReferencia}`)
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Metas"
        leftAction={null}
        rightActions={[
          {
            icon: <Edit3 className="w-5 h-5" />,
            label: 'Editar todas',
            onClick: handleEditAll
          }
        ]}
      />
      
      {/* Month Picker */}
      <MonthScrollPicker
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
        className="bg-white border-b border-gray-200"
      />
      
      {/* YTD Toggle */}
      <div className="flex justify-center py-4 bg-white border-b border-gray-200">
        <YTDToggle
          value={period}
          onChange={setPeriod}
        />
      </div>
      
      {/* Tracker Cards */}
      <div className="flex-1 overflow-y-auto p-5">
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-500">Carregando...</div>
          </div>
        ) : budgets.length > 0 ? (
          <div className="space-y-4">
            {budgets.map((budget) => {
              const mapping = GROUP_TO_CATEGORY[budget.grupo]
              if (!mapping) return null
              
              return (
                <TrackerCard
                  key={budget.grupo}
                  category={mapping.category}
                  categoryName={mapping.name}
                  frequency={period === 'month' ? 'Mensal' : 'Anual'}
                  spent={budget.gasto}
                  budget={budget.orcamento}
                  onClick={() => handleEditClick(budget)}
                />
              )
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="text-gray-500 text-center">
              <div className="font-semibold mb-2">Nenhum orçamento encontrado</div>
              <div className="text-sm">Configure suas metas para começar</div>
            </div>
          </div>
        )}
      </div>
      
      {/* Bottom Sheet de Edição */}
      {editingBudget && (
        <BudgetEditBottomSheet
          isOpen={isEditSheetOpen}
          onClose={() => setIsEditSheetOpen(false)}
          category={GROUP_TO_CATEGORY[editingBudget.grupo]?.category || 'outros'}
          categoryName={GROUP_TO_CATEGORY[editingBudget.grupo]?.name || editingBudget.grupo}
          currentBudget={editingBudget.orcamento}
          onSave={handleSaveBudget}
        />
      )}
    </div>
  )
}
