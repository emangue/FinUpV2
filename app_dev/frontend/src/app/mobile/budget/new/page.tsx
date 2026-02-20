'use client'

/**
 * Create/Edit Goal Page
 * Página para criar ou editar uma meta
 * 1º dropdown: Tipo (Despesa | Receita | Investimentos)
 * 2º dropdown: Grupo filtrado pela categoria
 */

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Save } from 'lucide-react'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { useGoals } from '@/features/goals/hooks/use-goals'
import { useGoalDetail } from '@/features/goals/hooks/use-goal-detail'
import { fetchGruposComCategoria } from '@/features/goals/services/goals-api'
import { GoalCreate, GoalUpdate } from '@/features/goals/types'
import { format } from 'date-fns'

const TIPOS_META = [
  { value: 'Despesa', label: 'Despesa' },
  { value: 'Receita', label: 'Receita' },
  { value: 'Investimentos', label: 'Investimentos' }
] as const

/** Mapeia categoria_geral do grupo para o tipo do 1º dropdown (Transferência → Despesa) */
function tipoParaFiltro(categoria_geral: string): string {
  return categoria_geral === 'Transferência' ? 'Despesa' : categoria_geral
}

function CreateEditGoalContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const goalId = searchParams.get('id')
  const isEdit = !!goalId
  
  const { addGoal, editGoal } = useGoals()
  const { goal, loading: loadingGoal } = useGoalDetail(goalId ? parseInt(goalId) : 0)
  const [gruposComCategoria, setGruposComCategoria] = React.useState<{ nome_grupo: string; categoria_geral: string }[]>([])
  
  const grupoFromUrl = searchParams.get('grupo')
  const mesFromUrl = searchParams.get('mes')
  
  const [formData, setFormData] = React.useState({
    tipo: '' as string,
    grupo: grupoFromUrl || '',
    valor_planejado: '',
    mes_referencia: mesFromUrl || format(new Date(), 'yyyy-MM'),
    replicarParaAnoTodo: false
  })
  
  const [saving, setSaving] = React.useState(false)
  const [errors, setErrors] = React.useState<Record<string, string>>({})
  
  // Carregar grupos com categoria
  React.useEffect(() => {
    fetchGruposComCategoria().then(setGruposComCategoria)
  }, [])
  
  // Preencher grupo/mes da URL (ex: /new?grupo=Casa&mes=2026-02)
  React.useEffect(() => {
    if (!grupoFromUrl && !mesFromUrl) return
    setFormData((prev) => {
      const next = { ...prev }
      if (grupoFromUrl) next.grupo = grupoFromUrl
      if (mesFromUrl) next.mes_referencia = mesFromUrl
      return next
    })
  }, [grupoFromUrl, mesFromUrl])
  
  // Inferir tipo quando grupo da URL existir em gruposComCategoria
  React.useEffect(() => {
    if (grupoFromUrl && gruposComCategoria.length > 0) {
      const cat = gruposComCategoria.find((g) => g.nome_grupo === grupoFromUrl)?.categoria_geral
      if (cat) {
        setFormData((prev) => ({ ...prev, tipo: tipoParaFiltro(cat) }))
      }
    }
  }, [grupoFromUrl, gruposComCategoria])
  
  // Grupos filtrados pelo tipo selecionado
  const gruposFiltrados = React.useMemo(() => {
    if (!formData.tipo) return []
    return gruposComCategoria
      .filter((g) => tipoParaFiltro(g.categoria_geral) === formData.tipo)
      .map((g) => g.nome_grupo)
      .sort()
  }, [gruposComCategoria, formData.tipo])
  
  // Carregar dados da meta se for edição
  React.useEffect(() => {
    if (isEdit && goal) {
      const cat = goal.categoria_geral || 'Despesa'
      const tipo = tipoParaFiltro(cat)
      setFormData((prev) => ({
        ...prev,
        tipo,
        grupo: goal.grupo,
        valor_planejado: goal.valor_planejado.toString(),
        mes_referencia: goal.mes_referencia
      }))
    }
  }, [isEdit, goal])
  
  const handleTipoChange = (tipo: string) => {
    setFormData({ ...formData, tipo, grupo: '' })
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.tipo) {
      newErrors.tipo = 'Selecione o tipo'
    }
    if (!formData.grupo.trim()) {
      newErrors.grupo = 'Selecione um grupo'
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
        await addGoal(data as GoalCreate, formData.replicarParaAnoTodo)
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
          {/* 1º dropdown: Tipo (Despesa | Receita | Investimentos) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo *
            </label>
            <select
              value={formData.tipo}
              onChange={(e) => handleTipoChange(e.target.value)}
              className={`w-full px-4 py-3 rounded-lg border ${
                errors.tipo ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white`}
            >
              <option value="">Selecione o tipo</option>
              {TIPOS_META.map((t) => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
            {errors.tipo && (
              <p className="text-red-500 text-sm mt-1">{errors.tipo}</p>
            )}
          </div>

          {/* 2º dropdown: Grupo filtrado pelo tipo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Grupo *
            </label>
            <select
              value={formData.grupo}
              onChange={(e) => setFormData({ ...formData, grupo: e.target.value })}
              disabled={!formData.tipo}
              className={`w-full px-4 py-3 rounded-lg border ${
                errors.grupo ? 'border-red-500' : 'border-gray-200'
              } focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white disabled:bg-gray-50 disabled:text-gray-500`}
            >
              <option value="">
                {formData.tipo ? 'Selecione um grupo' : 'Selecione o tipo primeiro'}
              </option>
              {[...new Set([...gruposFiltrados, ...(formData.grupo ? [formData.grupo] : [])])]
                .sort()
                .map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
            </select>
            {errors.grupo && (
              <p className="text-red-500 text-sm mt-1">{errors.grupo}</p>
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

          {/* Replicar para o ano todo - apenas na criação */}
          {!isEdit && (
            <div className="space-y-1">
              <label className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 bg-white cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.replicarParaAnoTodo}
                  onChange={(e) => setFormData({ ...formData, replicarParaAnoTodo: e.target.checked })}
                  className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm font-medium text-gray-700">
                  Replicar esta meta para o ano todo
                </span>
              </label>
              {formData.replicarParaAnoTodo && formData.mes_referencia && (
                <p className="text-xs text-gray-500 px-1">
                  Será criada do mês {formData.mes_referencia} até dezembro do mesmo ano
                </p>
              )}
            </div>
          )}
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
