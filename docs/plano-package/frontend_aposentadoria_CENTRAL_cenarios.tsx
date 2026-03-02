'use client'

/**
 * Central de Cenários - Sprint H
 * Lista cenários ativos, permite criar, editar nome e excluir.
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Pencil, Trash2, ChevronRight, ChevronDown, Plus, Star } from 'lucide-react'
import {
  getCenarios,
  updateCenario,
  deleteCenario,
} from '@/features/investimentos/services/investimentos-api'
import type { InvestimentoCenario } from '@/features/investimentos/types'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogAction,
  AlertDialogCancel,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'

const MESES = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
const RECORRENCIA_LABEL: Record<string, string> = {
  unico: 'único',
  trimestral: 'trimestral',
  semestral: 'semestral',
  anual: 'anual',
}

function formatCurrency(value: number | string): string {
  const n = typeof value === 'string' ? parseFloat(value) || 0 : value
  if (n >= 1_000_000) return `R$ ${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `R$ ${Math.round(n / 1_000)} mil`
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n)
}

/** Formato compacto evolução: "+15% YoY" ou "+25k YoY" */
function formatEvolucaoYoY(evolucaoValor: number, evolucaoTipo: 'percentual' | 'nominal'): string {
  if (evolucaoTipo === 'percentual') return `+${evolucaoValor}% YoY`
  if (evolucaoValor >= 1_000_000) return `+${(evolucaoValor / 1_000_000).toFixed(1)}M YoY`
  if (evolucaoValor >= 1_000) return `+${Math.round(evolucaoValor / 1_000)}k YoY`
  return `+R$ ${evolucaoValor} YoY`
}

/** Formato compacto: "R$ 15 mil, anual novembro" ou "R$ 15 mil, anual novembro (13º salário)" */
function formatExtraCompact(
  valor: number,
  recorrencia: string,
  mesAno: number,
  descricao?: string,
  evoluir?: boolean,
  evolucaoValor?: number,
  evolucaoTipo?: 'percentual' | 'nominal'
): string {
  const rec = RECORRENCIA_LABEL[recorrencia] ?? recorrencia
  const mes = MESES[Math.max(0, Math.min(11, mesAno - 1))]
  let base = `${formatCurrency(valor)}, ${rec} ${mes}`
  if (descricao?.trim()) base += ` (${descricao})`
  if (evoluir && evolucaoValor != null && evolucaoValor !== 0) {
    const tipo = evolucaoTipo ?? 'percentual'
    base += ` · ${formatEvolucaoYoY(evolucaoValor, tipo)}`
  }
  return base
}

function parseExtrasForDisplay(
  extrasJson: string | undefined
): Array<{
  valor: number
  recorrencia: string
  mesAno: number
  descricao?: string
  evoluir?: boolean
  evolucaoValor?: number
  evolucaoTipo?: 'percentual' | 'nominal'
}> {
  if (!extrasJson) return []
  try {
    const arr = JSON.parse(extrasJson)
    if (!Array.isArray(arr)) return []
    return arr.map((e: Record<string, unknown>) => ({
      valor: (e.valor as number) ?? 0,
      recorrencia: (e.recorrencia as string) ?? 'anual',
      mesAno: (e.mesAno as number) ?? 12,
      descricao: e.descricao as string | undefined,
      evoluir: e.evoluir as boolean | undefined,
      evolucaoValor: e.evolucaoValor as number | undefined,
      evolucaoTipo: (e.evolucaoTipo as 'percentual' | 'nominal') ?? 'percentual',
    }))
  } catch {
    return []
  }
}

/** Agrupa aportes_extraordinarios por (descricao, mês) e retorna linhas compactas */
function groupAportesToCompact(
  aportes: Array<{ id: number; mes_referencia: number; valor: string; descricao?: string }>,
  anomesInicio: number
): Array<{ label: string }> {
  const byKey = new Map<string, { valor: number; descricao: string; mesCal: number }>()
  for (const ap of aportes) {
    let y = Math.floor(anomesInicio / 100)
    let m = (anomesInicio % 100) + ap.mes_referencia - 1
    while (m > 12) { m -= 12; y += 1 }
    while (m < 1) { m += 12; y -= 1 }
    const mesCal = m
    const key = `${ap.descricao ?? 'Aporte'}|${mesCal}`
    const val = parseFloat(String(ap.valor)) || 0
    if (!byKey.has(key)) {
      byKey.set(key, { valor: val, descricao: ap.descricao ?? 'Aporte', mesCal })
    }
  }
  return [...byKey.values()]
    .sort((a, b) => a.mesCal - b.mesCal)
    .map((v) => ({
      label: `${formatCurrency(v.valor)}, anual ${MESES[v.mesCal - 1] ?? ''}${v.descricao ? ` (${v.descricao})` : ''}`,
    }))
}

interface CentralCenariosProps {
  cenarios: InvestimentoCenario[]
  onRefresh: () => void
}

export function CentralCenarios({ cenarios, onRefresh }: CentralCenariosProps) {
  const router = useRouter()
  const [editId, setEditId] = useState<number | null>(null)
  const [editNome, setEditNome] = useState('')
  const [deleteId, setDeleteId] = useState<number | null>(null)
  const [saving, setSaving] = useState(false)

  const handleEditName = (c: InvestimentoCenario) => {
    setEditId(c.id)
    setEditNome(c.nome_cenario || '')
  }

  const handleSaveName = async () => {
    if (!editId || !editNome.trim()) return
    setSaving(true)
    try {
      await updateCenario(editId, { nome_cenario: editNome.trim() })
      onRefresh()
      setEditId(null)
    } catch {
      // erro silencioso
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteId) return
    setSaving(true)
    try {
      await deleteCenario(deleteId)
      onRefresh()
      setDeleteId(null)
    } catch {
      // erro silencioso
    } finally {
      setSaving(false)
    }
  }

  const handleSetPrincipal = async (c: InvestimentoCenario) => {
    setSaving(true)
    try {
      await updateCenario(c.id, { principal: true })
      onRefresh()
    } catch {
      // erro silencioso
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900">Meus Cenários</h3>
      </div>

      <div className="space-y-3">
        {cenarios.map((c) => {
          const isPrincipal = c.id === (cenarios.find((x) => x.principal) ?? cenarios[0])?.id
          return (
          <Collapsible key={c.id} className="rounded-2xl border border-gray-200 bg-white overflow-hidden group">
            <div className="flex items-start gap-3 p-4">
              <CollapsibleTrigger asChild>
                <button type="button" className="shrink-0 p-1 -m-1 rounded-lg hover:bg-gray-100 transition-colors mt-0.5">
                  <ChevronDown className="w-5 h-5 text-gray-400 transition-transform group-data-[state=open]:rotate-180" />
                </button>
              </CollapsibleTrigger>
              <CollapsibleTrigger asChild>
                <div className="flex-1 min-w-0 flex flex-col gap-1 cursor-pointer hover:opacity-80 transition-opacity py-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-base font-semibold text-gray-900 truncate" title={c.nome_cenario || undefined}>
                      {c.nome_cenario || 'Sem nome'}
                    </span>
                    {isPrincipal && (
                      <span className="text-[10px] font-medium text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded shrink-0">
                        Padrão
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                    {c.idade_atual != null && (
                      <span>Idade {c.idade_atual} → {c.idade_aposentadoria ?? '?'} anos</span>
                    )}
                    {c.renda_mensal_alvo != null && c.renda_mensal_alvo !== '' && (
                      <span>• Meta {formatCurrency(parseFloat(String(c.renda_mensal_alvo)))}/mês</span>
                    )}
                  </div>
                </div>
              </CollapsibleTrigger>
              <div className="flex items-center gap-1 shrink-0 relative z-10 self-center" onClick={(e) => e.stopPropagation()}>
                <button
                  type="button"
                  onPointerDown={(e) => e.stopPropagation()}
                  onClick={(e) => {
                    e.stopPropagation()
                    e.preventDefault()
                    if (!isPrincipal && !saving) handleSetPrincipal(c)
                  }}
                  disabled={isPrincipal || saving}
                  className={`p-2 rounded-lg transition-colors touch-manipulation ${
                    isPrincipal
                      ? 'text-amber-500'
                      : 'text-gray-300 hover:text-amber-500 hover:bg-amber-50'
                  }`}
                  aria-label={isPrincipal ? 'Cenário padrão' : 'Definir como padrão'}
                  title={isPrincipal ? 'Cenário padrão (usado em todo o app)' : 'Definir como padrão'}
                >
                  <Star className={`w-5 h-5 ${isPrincipal ? 'fill-amber-500' : ''}`} />
                </button>
                <button
                  onClick={() => handleEditName(c)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
                  aria-label="Editar nome"
                >
                  <Pencil className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setDeleteId(c.id)}
                  className="p-2 rounded-lg hover:bg-red-50 text-red-600"
                  aria-label="Excluir cenário"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => router.push(`/mobile/personalizar-plano?id=${c.id}`)}
                  className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
                  aria-label="Editar cenário"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
            <CollapsibleContent>
              <div className="px-4 pb-4 pt-0 border-t border-gray-100">
                <div className="grid grid-cols-2 gap-2 pt-3 text-xs">
                  <div className="text-gray-500">Patrimônio inicial</div>
                  <div className="text-right font-medium text-gray-900">
                    {formatCurrency(parseFloat(String(c.patrimonio_inicial)) || 0)}
                  </div>
                  <div className="text-gray-500">Aporte mensal</div>
                  <div className="text-right font-medium text-gray-900">
                    {formatCurrency(parseFloat(String(c.aporte_mensal)) || 0)}
                  </div>
                  {c.retorno_aa != null && c.retorno_aa !== '' && (
                    <>
                      <div className="text-gray-500">Retorno anual</div>
                      <div className="text-right font-medium text-gray-900">{c.retorno_aa}% a.a.</div>
                    </>
                  )}
                  {c.inflacao_aa != null && c.inflacao_aa !== '' && (
                    <>
                      <div className="text-gray-500">Inflação</div>
                      <div className="text-right font-medium text-gray-900">{c.inflacao_aa}% a.a.</div>
                    </>
                  )}
                  <div className="text-gray-500 col-span-2">Aportes extraordinários</div>
                  <div className="col-span-2">
                    {(() => {
                      const extras = parseExtrasForDisplay(c.extras_json)
                      const anomesInicio = c.anomes_inicio ?? new Date().getFullYear() * 100 + (new Date().getMonth() + 1)
                      const fromAportes = c.aportes_extraordinarios?.length
                        ? groupAportesToCompact(c.aportes_extraordinarios, anomesInicio)
                        : []
                      const items = extras.length > 0
                        ? extras.map((e, i) => ({
                            key: `ext-${i}-${e.valor}-${e.mesAno}`,
                            label: formatExtraCompact(
                              e.valor,
                              e.recorrencia,
                              e.mesAno,
                              e.descricao,
                              e.evoluir,
                              e.evolucaoValor,
                              e.evolucaoTipo
                            ),
                          }))
                        : fromAportes.map((a, i) => ({ key: `ap-${i}`, label: a.label }))
                      if (items.length === 0) {
                        return <span className="text-xs text-gray-400">Nenhum programado</span>
                      }
                      return (
                        <div className="space-y-1 text-xs text-gray-700">
                          {items.map(({ key, label }) => (
                            <div key={key}>{label}</div>
                          ))}
                        </div>
                      )
                    })()}
                  </div>
                </div>
                <button
                  onClick={() => router.push(`/mobile/personalizar-plano?id=${c.id}`)}
                  className="w-full mt-3 py-2.5 text-xs font-medium text-gray-600 hover:text-gray-900 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors flex items-center justify-center gap-1.5"
                >
                  Editar plano completo
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </CollapsibleContent>
          </Collapsible>
          )
        })}
      </div>

      <button
        onClick={() => router.push('/mobile/personalizar-plano')}
        className="w-full py-4 bg-gray-900 text-white rounded-2xl text-sm font-semibold
                   hover:bg-gray-800 active:scale-[0.98] transition-all
                   flex items-center justify-center gap-2"
      >
        <Plus className="w-5 h-5" />
        Novo Cenário
      </button>

      {/* Dialog Editar Nome */}
      <Dialog open={editId != null} onOpenChange={(o) => !o && setEditId(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Editar nome do cenário</DialogTitle>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="nome-cenario">Nome</Label>
            <Input
              id="nome-cenario"
              value={editNome}
              onChange={(e) => setEditNome(e.target.value)}
              placeholder="Ex: Plano Conservador"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditId(null)}>
              Cancelar
            </Button>
            <Button onClick={handleSaveName} disabled={saving || !editNome.trim()}>
              {saving ? 'Salvando...' : 'Salvar'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* AlertDialog Excluir */}
      <AlertDialog open={deleteId != null} onOpenChange={(o) => !o && setDeleteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir cenário?</AlertDialogTitle>
            <AlertDialogDescription>
              O cenário será desativado e não aparecerá mais na lista. Você pode criar um novo
              cenário a qualquer momento.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-red-600 hover:bg-red-700"
              disabled={saving}
            >
              {saving ? 'Excluindo...' : 'Excluir'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
