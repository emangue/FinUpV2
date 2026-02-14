'use client'

/**
 * Create/Edit Goal Page
 * Página para criar ou editar uma meta
 */

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { ArrowLeft, Save } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { useGoals } from '@/features/goals/hooks/use-goals'
import { useGoalDetail } from '@/features/goals/hooks/use-goal-detail'
import { GoalCreate, GoalUpdate } from '@/features/goals/types'
import { format } from 'date-fns'

function CreateEditGoalContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const goalId = searchParams.get('id')
  const isEdit = !!goalId
  
  const { addGoal, editGoal } = useGoals()
  const { goal, loading: loadingGoal } = useGoalDetail(goalId ? parseInt(goalId) : 0)
  
  const [formData, setFormData] = React.useState({
    grupo: '',
    categoria_geral: '',
    valor_planejado: '',
    mes_referencia: format(new Date(), 'yyyy-MM')
  })
  
  const [saving, setSaving] = React.useState(false)
  const [errors, setErrors] = React.useState<Record<string, string>>({})
  
  // Carregar dados da meta se for edição
  React.useEffect(() => {
    if (isEdit && goal) {
      setFormData({
        grupo: goal.grupo,
        categoria_geral: goal.grupo, // Mesmo valor de grupo
        valor_planejado: goal.valor_planejado.toString(),
        mes_referencia: goal.mes_referencia
      })
    }
  }, [isEdit, goal])
  
  const handleBack = () => {
    router.back()
  }
  
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.grupo.trim()) {
      newErrors.grupo = 'Categoria é obrigatória'
    }
    
    const valor = parseFloat(formData.valor_planejado)
    if (!formData.valor_planejado || isNaN(valor) || valor <= 0) {
      newErrors.valor_planejado = 'Valor deve ser maior que zero'
    }
    
    if (!formData.mes_referencia) {
      newErrors.mes_referencia = 'Mês de referência é obrigatório'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    try {
      setSaving(true)
      
      const data: GoalCreate | GoalUpdate = {
        grupo: formData.grupo.trim(),
        valor_planejado: parseFloat(formData.valor_planejado),
        mes_referencia: formData.mes_referencia
      }
      
      if (isEdit && goalId) {
        await editGoal(parseInt(goalId), data)
      } else {
        await addGoal(data as GoalCreate)
      }
      
      router.push('/mobile/budget')
    } catch (error) {
      console.error('Erro ao salvar meta:', error)
      alert('Erro ao salvar meta. Tente novamente.')
    } finally {
      setSaving(false)
    }
  }
  
  if (isEdit && loadingGoal) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-gray-500">Carregando...</div>
      </div>
    )
  }
  
  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title={isEdit ? 'Editar Meta' : 'Nova Meta'}
        leftAction="back"
        rightActions={[]}
      />
      
      {/* Form */}
      <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5">
        <div className="space-y-5">
          {/* Categoria */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categoria *
            </label>
            <input
              type="text"
              value={formData.grupo}
              onChange={(e) => setFormData({ ...formData, grupo: e.target.value })}
              placeholder="Ex: Alimentação, Transporte, Lazer"
              className={`w-full px-4 py-3 rounded-lg border ${
                errors.categoria_geral ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.categoria_geral && (
              <p className="text-red-500 text-sm mt-1">{errors.categoria_geral}</p>
            )}
          </div>
          
          {/* Valor Planejado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Valor Planejado *
            </label>
            <div className="relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">
                R$
              </span>
              <input
                type="number"
                step="0.01"
                value={formData.valor_planejado}
                onChange={(e) => setFormData({ ...formData, valor_planejado: e.target.value })}
                placeholder="0,00"
                className={`w-full pl-12 pr-4 py-3 rounded-lg border ${
                  errors.valor_planejado ? 'border-red-500' : 'border-gray-200'
                } focus:outline-none focus:ring-2 focus:ring-blue-500`}
              />
            </div>
            {errors.valor_planejado && (
              <p className="text-red-500 text-sm mt-1">{errors.valor_planejado}</p>
            )}
          </div>
          
          {/* Mês de Referência */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mês de Referência *
            </label>
            <input
              type="month"
              value={formData.mes_referencia}
              onChange={(e) => setFormData({ ...formData, mes_referencia: e.target.value })}
              className={`w-full px-4 py-3 rounded-lg border ${
                errors.mes_referencia ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.mes_referencia && (
              <p className="text-red-500 text-sm mt-1">{errors.mes_referencia}</p>
            )}
          </div>
        </div>
      </form>
      
      {/* Bottom Button */}
      <div className="p-5 bg-white border-t border-gray-200">
        <button
          onClick={handleSubmit}
          disabled={saving}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <Save className="w-5 h-5" />
          {saving ? 'Salvando...' : isEdit ? 'Salvar Alterações' : 'Criar Meta'}
        </button>
      </div>
    </div>
  )
}

export default function CreateEditGoalPage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col h-screen bg-gray-50 items-center justify-center">
        <div className="text-gray-500">Carregando...</div>
      </div>
    }>
      <CreateEditGoalContent />
    </Suspense>
  )
}
