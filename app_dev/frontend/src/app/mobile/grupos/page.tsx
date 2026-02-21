'use client'

/**
 * Central de Grupos - Mobile (Sprint C)
 * Tela para gerenciar grupos: listar, editar cor, categoria_geral, tipo_gasto
 * Paleta de 11 cores em gradiente azul
 */

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { ChevronLeft, Palette, Pencil } from 'lucide-react'
import { useRequireAuth } from '@/core/hooks/use-require-auth'
import { GOAL_COLORS } from '@/features/goals/lib/colors'

interface Grupo {
  id: number
  nome_grupo: string
  tipo_gasto_padrao: string
  categoria_geral: string
  cor?: string | null
}

interface Opcoes {
  tipos_gasto: string[]
  categorias: string[]
  paleta_cores?: string[]
}

export default function GruposMobilePage() {
  const router = useRouter()
  const isAuth = useRequireAuth()
  const [grupos, setGrupos] = useState<Grupo[]>([])
  const [opcoes, setOpcoes] = useState<Opcoes | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editingGrupo, setEditingGrupo] = useState<Grupo | null>(null)
  const [saving, setSaving] = useState(false)

  const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}/grupos`
  const paleta = opcoes?.paleta_cores ?? GOAL_COLORS

  useEffect(() => {
    if (!isAuth) return
    loadData()
  }, [isAuth])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const [resGrupos, resOpcoes] = await Promise.all([
        fetchWithAuth(BASE_URL),
        fetchWithAuth(`${BASE_URL}/opcoes`),
      ])
      if (!resGrupos.ok) throw new Error('Erro ao carregar grupos')
      if (!resOpcoes.ok) throw new Error('Erro ao carregar opções')
      const dataGrupos = await resGrupos.json()
      const dataOpcoes = await resOpcoes.json()
      setGrupos(dataGrupos.grupos ?? [])
      setOpcoes(dataOpcoes)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveGrupo = async (grupo: Grupo, updates: Partial<Grupo>) => {
    try {
      setSaving(true)
      const res = await fetchWithAuth(`${BASE_URL}/${grupo.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Erro ao salvar')
      }
      setEditingGrupo(null)
      loadData()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const getGrupoColor = (grupo: Grupo, index: number) =>
    grupo.cor || paleta[index % paleta.length]

  if (!isAuth) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileHeader title="Grupos" leftAction="logo" />
        <div className="flex items-center justify-center h-[calc(100vh-64px)]">
          <p className="text-gray-600">Verificando autenticação...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      <MobileHeader
        title="Central de Grupos"
        leftAction="back"
        onBack={() => router.push('/mobile/profile')}
      />

      <div className="p-5 space-y-4">
        <p className="text-sm text-gray-500">
          Gerencie cores, categorias e tipos de gasto dos seus grupos.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-xl text-sm">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600" />
          </div>
        ) : (
          <div className="space-y-2">
            {grupos.map((grupo, idx) => (
              <div
                key={grupo.id}
                className="bg-white rounded-2xl border border-gray-200 p-4 shadow-sm"
              >
                {editingGrupo?.id === grupo.id ? (
                  <EditGrupoForm
                    grupo={grupo}
                    paleta={paleta}
                    opcoes={opcoes}
                    saving={saving}
                    onSave={(updates) => handleSaveGrupo(grupo, updates)}
                    onCancel={() => setEditingGrupo(null)}
                  />
                ) : (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className="w-10 h-10 rounded-xl shrink-0"
                        style={{ backgroundColor: getGrupoColor(grupo, idx) }}
                      />
                      <div className="min-w-0">
                        <p className="font-semibold text-gray-900 truncate">
                          {grupo.nome_grupo}
                        </p>
                        <p className="text-xs text-gray-500">
                          {grupo.tipo_gasto_padrao} · {grupo.categoria_geral}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => setEditingGrupo(grupo)}
                      className="p-2 rounded-lg hover:bg-gray-100"
                      aria-label="Editar grupo"
                    >
                      <Pencil className="w-5 h-5 text-gray-500" />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function EditGrupoForm({
  grupo,
  paleta,
  opcoes,
  saving,
  onSave,
  onCancel,
}: {
  grupo: Grupo
  paleta: readonly string[]
  opcoes: Opcoes | null
  saving: boolean
  onSave: (updates: Partial<Grupo>) => void
  onCancel: () => void
}) {
  const [cor, setCor] = useState(grupo.cor || paleta[0])
  const [tipoGasto, setTipoGasto] = useState(grupo.tipo_gasto_padrao)
  const [categoria, setCategoria] = useState(grupo.categoria_geral)

  const tipos = opcoes?.tipos_gasto ?? ['Fixo', 'Ajustável']
  const categorias = opcoes?.categorias ?? ['Despesa', 'Receita', 'Investimentos', 'Transferência Entre Contas']

  return (
    <div className="space-y-4">
      <p className="font-semibold text-gray-900">{grupo.nome_grupo}</p>

      <div>
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-2">
          Cor
        </label>
        <div className="flex flex-wrap gap-2">
          {paleta.map((hex) => (
            <button
              key={hex}
              type="button"
              onClick={() => setCor(hex)}
              className={`w-9 h-9 rounded-full border-2 transition-all ${
                cor === hex ? 'border-gray-900 scale-110' : 'border-transparent'
              }`}
              style={{ backgroundColor: hex }}
              aria-label={`Cor ${hex}`}
            />
          ))}
        </div>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">
          Tipo de Gasto
        </label>
        <select
          value={tipoGasto}
          onChange={(e) => setTipoGasto(e.target.value)}
          className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"
        >
          {tipos.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500 uppercase tracking-wide block mb-1">
          Categoria Geral
        </label>
        <select
          value={categoria}
          onChange={(e) => setCategoria(e.target.value)}
          className="w-full rounded-xl border border-gray-200 px-4 py-2.5 text-sm"
        >
          {categorias.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      <div className="flex gap-2 pt-2">
        <button
          onClick={onCancel}
          className="flex-1 py-2.5 rounded-xl border border-gray-200 font-medium text-gray-700"
        >
          Cancelar
        </button>
        <button
          onClick={() =>
            onSave({
              cor: cor || null,
              tipo_gasto_padrao: tipoGasto,
              categoria_geral: categoria,
            })
          }
          disabled={saving}
          className="flex-1 py-2.5 rounded-xl bg-gray-900 text-white font-medium disabled:opacity-50"
        >
          {saving ? 'Salvando...' : 'Salvar'}
        </button>
      </div>
    </div>
  )
}
