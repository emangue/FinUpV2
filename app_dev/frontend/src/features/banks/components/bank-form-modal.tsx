"use client"

import * as React from "react"
import { BankCompatibility } from '../types'
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

interface BankFormModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  bank?: BankCompatibility | null
  onSave: (data: { status: 'OK' | 'WIP' | 'TBD' }) => Promise<void>
}

export function BankFormModal({ open, onOpenChange, bank, onSave }: BankFormModalProps) {
  const [status, setStatus] = React.useState<'OK' | 'WIP' | 'TBD'>('TBD')
  const [saving, setSaving] = React.useState(false)

  React.useEffect(() => {
    if (bank) {
      setStatus(bank.status)
    } else {
      setStatus('TBD')
    }
  }, [bank, open])

  const handleSave = async () => {
    try {
      setSaving(true)
      await onSave({ status })
      onOpenChange(false)
    } catch (error) {
      console.error('Erro ao salvar:', error)
      const message = error instanceof Error ? error.message : 'Erro ao salvar banco'
      alert(message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Editar Status</DialogTitle>
          <DialogDescription>
            Atualize o status de compatibilidade para {bank?.bank_name} - {bank?.file_format}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label>Banco</Label>
            <div className="text-sm font-medium">{bank?.bank_name}</div>
          </div>

          <div className="grid gap-2">
            <Label>Formato</Label>
            <div className="text-sm font-medium">{bank?.file_format}</div>
          </div>

          <div className="grid gap-2">
            <Label htmlFor="status">Status</Label>
            <Select value={status} onValueChange={(value: any) => setStatus(value)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="OK">OK - Funcionando</SelectItem>
                <SelectItem value="WIP">WIP - Em Desenvolvimento</SelectItem>
                <SelectItem value="TBD">TBD - A Fazer</SelectItem>
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
