"use client"

import * as React from "react"
import { toast } from 'sonner'
import { fetchWithAuth } from '@/core/utils/api-client'  // ✅ FASE 3 - Autenticação obrigatória
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Plus, Trash2 } from "lucide-react"
import { AddGroupModal } from "./add-group-modal"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

interface Transaction {
  IdTransacao: string
  Data: string
  Estabelecimento: string
  Valor: number
  ValorPositivo: number
  TipoTransacao: string
  Grupo: string
  SubGrupo: string
  TipoGasto: string
  origem_classificacao: string
  MesFatura: string
  banco_origem: string
  NomeCartao: string
  CategoriaGeral: string
}

interface EditTransactionModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  transaction: Transaction | null
  onSave: () => void
}

export function EditTransactionModal({
  open,
  onOpenChange,
  transaction,
  onSave
}: EditTransactionModalProps) {
  const [grupo, setGrupo] = React.useState("")
  const [subgrupo, setSubgrupo] = React.useState("")
  const [grupos, setGrupos] = React.useState<string[]>([])
  const [subgruposPorGrupo, setSubgruposPorGrupo] = React.useState<Record<string, string[]>>({})
  const [loading, setLoading] = React.useState(false)
  const [deleting, setDeleting] = React.useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [addGroupOpen, setAddGroupOpen] = React.useState(false)
  const [addGroupType, setAddGroupType] = React.useState<'grupo' | 'subgrupo'>('grupo')

  // Subgrupos filtrados pelo grupo selecionado
  const subgruposDisponiveis = React.useMemo(() => {
    if (!grupo) return []
    return subgruposPorGrupo[grupo] || []
  }, [grupo, subgruposPorGrupo])

  React.useEffect(() => {
    if (transaction) {
      setGrupo(transaction.Grupo || "")
      setSubgrupo(transaction.SubGrupo || "")
    }
  }, [transaction])

  React.useEffect(() => {
    fetchGrupos()
  }, [])

  const fetchGrupos = async () => {
    try {
      const response = await fetchWithAuth('/api/categories/grupos-subgrupos')
      if (response.ok) {
        const data = await response.json()
        setGrupos(data.grupos || [])
        setSubgruposPorGrupo(data.subgruposPorGrupo || {})
      }
    } catch (error) {
      console.error('Erro ao buscar grupos:', error)
    }
  }

  const handleSave = async () => {
    if (!transaction) return

    setLoading(true)
    try {
      const response = await fetchWithAuth(`/api/transactions/update/${transaction.IdTransacao}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ GRUPO: grupo, SUBGRUPO: subgrupo })
      })

      if (response.ok) {
        onSave()
        onOpenChange(false)
      } else {
        const errorData = await response.json()
        console.error('Erro na resposta:', errorData)
        toast.error('Erro ao salvar alterações')
      }
    } catch (error) {
      console.error('Erro ao salvar:', error)
      toast.error('Erro ao salvar alterações')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!transaction) return

    setDeleting(true)
    try {
      const response = await fetchWithAuth(`/api/transactions/${transaction.IdTransacao}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        onSave() // Atualiza a lista
        onOpenChange(false) // Fecha o modal
        setDeleteDialogOpen(false) // Fecha o dialog de confirmação
      } else {
        const errorData = await response.json()
        console.error('Erro na resposta:', errorData)
        toast.error('Erro ao excluir transação')
      }
    } catch (error) {
      console.error('Erro ao excluir:', error)
      toast.error('Erro ao excluir transação')
    } finally {
      setDeleting(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    if (dateString && dateString.includes('/')) {
      return dateString
    }
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR')
    } catch {
      return dateString
    }
  }

  const handleAddGroup = (tipo: 'grupo' | 'subgrupo') => {
    setAddGroupType(tipo)
    setAddGroupOpen(true)
  }

  const handleGroupAdded = () => {
    fetchGrupos()
  }

  if (!transaction) return null

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Editar Transação</DialogTitle>
            <DialogDescription>
              Ajuste o grupo e subgrupo desta transação
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Detalhes da transação */}
            <div className="grid grid-cols-2 gap-4 p-4 border rounded-lg bg-muted/50">
              <div>
                <Label className="text-xs text-muted-foreground">Data</Label>
                <p className="font-medium">{formatDate(transaction.Data)}</p>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Valor</Label>
                <p className={`font-medium ${transaction.Valor >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(transaction.Valor)}
                </p>
              </div>
              <div className="col-span-2">
                <Label className="text-xs text-muted-foreground">Estabelecimento</Label>
                <p className="font-medium">{transaction.Estabelecimento}</p>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Tipo</Label>
                <p className="text-sm">{transaction.TipoTransacao}</p>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Tipo de Gasto</Label>
                <p className="text-sm">{transaction.TipoGasto}</p>
              </div>
              {/* Mostrar Mês da Fatura apenas para Cartão de Crédito */}
              {transaction.TipoTransacao === 'Cartão de Crédito' && transaction.MesFatura && (
                <div className="col-span-2">
                  <Label className="text-xs text-muted-foreground">Mês da Fatura</Label>
                  <p className="text-sm font-medium text-blue-600">
                    {transaction.MesFatura.substring(4, 6)}/{transaction.MesFatura.substring(0, 4)}
                  </p>
                </div>
              )}
            </div>

            {/* Grupo */}
            <div className="grid gap-2">
              <Label htmlFor="grupo">Grupo</Label>
              <div className="flex gap-2">
                <Select value={grupo} onValueChange={setGrupo}>
                  <SelectTrigger id="grupo" className="flex-1">
                    <SelectValue placeholder="Selecione um grupo" />
                  </SelectTrigger>
                  <SelectContent>
                    {grupos.map((g) => (
                      <SelectItem key={g} value={g}>
                        {g}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => handleAddGroup('grupo')}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Subgrupo */}
            <div className="grid gap-2">
              <Label htmlFor="subgrupo">Subgrupo</Label>
              <div className="flex gap-2">
                <Select value={subgrupo} onValueChange={setSubgrupo} disabled={!grupo}>
                  <SelectTrigger id="subgrupo" className="flex-1">
                    <SelectValue placeholder={grupo ? "Selecione um subgrupo" : "Selecione um grupo primeiro"} />
                  </SelectTrigger>
                  <SelectContent>
                    {subgruposDisponiveis.map((s) => (
                      <SelectItem key={s} value={s}>
                        {s}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  onClick={() => handleAddGroup('subgrupo')}
                >
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          <DialogFooter className="flex justify-between items-center sm:justify-between">
            <Button 
              variant="destructive" 
              size="icon" 
              onClick={() => setDeleteDialogOpen(true)}
              disabled={loading || deleting}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => onOpenChange(false)} disabled={deleting}>
                Cancelar
              </Button>
              <Button onClick={handleSave} disabled={loading || deleting}>
                {loading ? 'Salvando...' : 'Salvar Alterações'}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir Transação</AlertDialogTitle>
            <AlertDialogDescription>
              Tem certeza que deseja excluir esta transação? Esta ação não pode ser desfeita.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete} className="bg-red-600 hover:bg-red-700">
              {deleting ? 'Excluindo...' : 'Excluir'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AddGroupModal
        open={addGroupOpen}
        onOpenChange={setAddGroupOpen}
        tipo={addGroupType}
        onSuccess={handleGroupAdded}
      />
    </>
  )
}
