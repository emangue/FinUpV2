'use client'

/**
 * Central de Cenários - Sprint H
 * Lista cenários ativos, permite criar, editar nome e excluir.
 */

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Pencil, Trash2, ChevronRight, Plus } from 'lucide-react'
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

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900">Meus Cenários</h3>
      </div>

      <div className="space-y-3">
        {cenarios.map((c) => (
          <div
            key={c.id}
            className="rounded-2xl border border-gray-200 bg-white p-4 flex items-center gap-3"
          >
            <div className="flex-1 min-w-0">
              <p className="text-base font-semibold text-gray-900 truncate">
                {c.nome_cenario || 'Sem nome'}
              </p>
              <div className="flex flex-wrap gap-2 mt-1 text-xs text-gray-500">
                {c.idade_atual != null && (
                  <span>Idade {c.idade_atual} → {c.idade_aposentadoria ?? '?'} anos</span>
                )}
                {c.renda_mensal_alvo != null && c.renda_mensal_alvo !== '' && (
                  <span>• Meta {formatCurrency(parseFloat(String(c.renda_mensal_alvo)))}/mês</span>
                )}
              </div>
            </div>
            <div className="flex items-center gap-1 shrink-0">
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
        ))}
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
