"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface AddGroupModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  tipo: 'grupo' | 'subgrupo'
  onSuccess: () => void
}

export function AddGroupModal({
  open,
  onOpenChange,
  tipo,
  onSuccess
}: AddGroupModalProps) {
  const [nome, setNome] = React.useState("")
  const [loading, setLoading] = React.useState(false)

  const handleSave = async () => {
    if (!nome.trim()) {
      alert('Por favor, insira um nome')
      return
    }

    setLoading(true)
    try {
      const response = await fetch('/api/grupos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo, nome: nome.trim() })
      })

      if (response.ok) {
        setNome("")
        onSuccess()
        onOpenChange(false)
      } else {
        alert('Erro ao criar ' + (tipo === 'grupo' ? 'grupo' : 'subgrupo'))
      }
    } catch (error) {
      console.error('Erro ao criar:', error)
      alert('Erro ao criar ' + (tipo === 'grupo' ? 'grupo' : 'subgrupo'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            Adicionar Novo {tipo === 'grupo' ? 'Grupo' : 'Subgrupo'}
          </DialogTitle>
          <DialogDescription>
            Crie um novo {tipo === 'grupo' ? 'grupo' : 'subgrupo'} para categorizar suas transações.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="nome">Nome do {tipo === 'grupo' ? 'Grupo' : 'Subgrupo'}</Label>
            <Input
              id="nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              placeholder={`Ex: ${tipo === 'grupo' ? 'Lazer, Saúde, Educação' : 'Cinema, Academia, Cursos'}`}
            />
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancelar
          </Button>
          <Button onClick={handleSave} disabled={loading || !nome.trim()}>
            {loading ? 'Criando...' : 'Criar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
