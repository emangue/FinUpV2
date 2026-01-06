"use client"

import * as React from "react"
import { Category } from '../types'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface CategoryFormModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  category?: Category | null
  onSave: (data: { GRUPO: string; SUBGRUPO: string; TipoGasto: string }) => Promise<void>
}

const TIPO_GASTO_OPTIONS = [
  'Ajustável',
  'Ajustável - Delivery',
  'Ajustável - Tech',
  'Ajustável - Saídas',
  'Essencial',
  'Fixo',
  'Investimento',
  'Receita'
]

export function CategoryFormModal({ open, onOpenChange, category, onSave }: CategoryFormModalProps) {
  const [grupo, setGrupo] = React.useState('')
  const [subgrupo, setSubgrupo] = React.useState('')
  const [tipoGasto, setTipoGasto] = React.useState('')
  const [saving, setSaving] = React.useState(false)

  React.useEffect(() => {
    if (category) {
      setGrupo(category.GRUPO)
      setSubgrupo(category.SUBGRUPO)
      setTipoGasto(category.TipoGasto)
    } else {
      setGrupo('')
      setSubgrupo('')
      setTipoGasto('')
    }
  }, [category, open])

  const handleSave = async () => {
    if (!grupo.trim() || !subgrupo.trim() || !tipoGasto.trim()) {
      alert('Todos os campos são obrigatórios')
      return
    }

    try {
      setSaving(true)
      await onSave({
        GRUPO: grupo.trim(),
        SUBGRUPO: subgrupo.trim(),
        TipoGasto: tipoGasto.trim()
      })
      onOpenChange(false)
    } catch (error) {
      console.error('Erro ao salvar:', error)
      alert('Erro ao salvar categoria')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {category ? 'Editar Categoria' : 'Nova Categoria'}
          </DialogTitle>
          <DialogDescription>
            {category ? 'Atualize os dados da categoria' : 'Adicione uma nova categoria de transação'}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="grupo">Grupo</Label>
            <Input
              id="grupo"
              value={grupo}
              onChange={(e) => setGrupo(e.target.value)}
              placeholder="Ex: Alimentação"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="subgrupo">Subgrupo</Label>
            <Input
              id="subgrupo"
              value={subgrupo}
              onChange={(e) => setSubgrupo(e.target.value)}
              placeholder="Ex: Almoço"
            />
          </div>

          <div className="grid gap-2">
            <Label htmlFor="tipoGasto">Tipo de Gasto</Label>
            <Select value={tipoGasto} onValueChange={setTipoGasto}>
              <SelectTrigger>
                <SelectValue placeholder="Selecione o tipo" />
              </SelectTrigger>
              <SelectContent>
                {TIPO_GASTO_OPTIONS.map(tipo => (
                  <SelectItem key={tipo} value={tipo}>{tipo}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
            Cancelar
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Salvando...' : 'Salvar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
