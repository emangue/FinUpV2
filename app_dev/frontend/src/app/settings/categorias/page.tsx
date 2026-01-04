"use client"

import * as React from "react"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Plus, Edit } from "lucide-react"

interface Marcacao {
  id: number
  GRUPO: string
  SUBGRUPO: string
  TipoGasto: string
}

export default function CategoriasPage() {
  const [marcacoes, setMarcacoes] = React.useState<Marcacao[]>([])
  const [loadingMarcacoes, setLoadingMarcacoes] = React.useState(true)
  const [marcacaoModalOpen, setMarcacaoModalOpen] = React.useState(false)
  const [marcacaoGrupo, setMarcacaoGrupo] = React.useState('')
  const [marcacaoSubgrupo, setMarcacaoSubgrupo] = React.useState('')
  const [marcacaoTipoGasto, setMarcacaoTipoGasto] = React.useState('')
  const [editingMarcacao, setEditingMarcacao] = React.useState<Marcacao | null>(null)

  React.useEffect(() => {
    fetchMarcacoes()
  }, [])

  const fetchMarcacoes = async () => {
    try {
      setLoadingMarcacoes(true)
      const response = await fetch('/api/marcacoes')
      if (response.ok) {
        const data = await response.json()
        setMarcacoes(data)
      }
    } catch (error) {
      console.error('Erro ao buscar marcações:', error)
    } finally {
      setLoadingMarcacoes(false)
    }
  }

  const handleAddMarcacao = () => {
    setMarcacaoGrupo('')
    setMarcacaoSubgrupo('')
    setMarcacaoTipoGasto('')
    setEditingMarcacao(null)
    setMarcacaoModalOpen(true)
  }

  const handleEditMarcacao = (marc: Marcacao) => {
    setEditingMarcacao(marc)
    setMarcacaoGrupo(marc.GRUPO)
    setMarcacaoSubgrupo(marc.SUBGRUPO)
    setMarcacaoTipoGasto(marc.TipoGasto)
    setMarcacaoModalOpen(true)
  }

  const handleSaveMarcacao = async () => {
    if (!marcacaoGrupo.trim() || !marcacaoSubgrupo.trim() || !marcacaoTipoGasto.trim()) {
      alert('Todos os campos são obrigatórios')
      return
    }

    try {
      const url = editingMarcacao ? `/api/marcacoes/${editingMarcacao.id}` : '/api/marcacoes'
      const method = editingMarcacao ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          GRUPO: marcacaoGrupo.trim(),
          SUBGRUPO: marcacaoSubgrupo.trim(),
          TipoGasto: marcacaoTipoGasto.trim()
        })
      })

      if (response.ok) {
        fetchMarcacoes()
        setMarcacaoModalOpen(false)
      } else {
        const error = await response.json()
        alert(error.error || 'Erro ao salvar')
      }
    } catch (error) {
      console.error('Erro ao salvar marcação:', error)
      alert('Erro ao salvar marcação')
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Gestão de Categorias</h1>
            <p className="text-muted-foreground">
              Gerencie as categorias de classificação de transações
            </p>
          </div>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Base de Marcações</CardTitle>
              <CardDescription>
                {marcacoes.length} marcações cadastradas
              </CardDescription>
            </div>
            <Button onClick={handleAddMarcacao}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Marcação
            </Button>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>GRUPO</TableHead>
                  <TableHead>SUBGRUPO</TableHead>
                  <TableHead>Tipo de Gasto</TableHead>
                  <TableHead className="w-[100px]">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {marcacoes.map((marc) => (
                  <TableRow key={marc.id}>
                    <TableCell className="font-medium">{marc.GRUPO}</TableCell>
                    <TableCell>{marc.SUBGRUPO}</TableCell>
                    <TableCell>{marc.TipoGasto}</TableCell>
                    <TableCell className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditMarcacao(marc)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Dialog open={marcacaoModalOpen} onOpenChange={setMarcacaoModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingMarcacao ? 'Editar' : 'Adicionar'} Marcação
              </DialogTitle>
              <DialogDescription>
                {editingMarcacao ? 'Altere' : 'Insira'} os dados da marcação (GRUPO, SUBGRUPO e Tipo de Gasto)
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="marcGrupo">GRUPO</Label>
                <Input
                  id="marcGrupo"
                  value={marcacaoGrupo}
                  onChange={(e) => setMarcacaoGrupo(e.target.value)}
                  placeholder="Ex: Alimentação"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marcSubgrupo">SUBGRUPO</Label>
                <Input
                  id="marcSubgrupo"
                  value={marcacaoSubgrupo}
                  onChange={(e) => setMarcacaoSubgrupo(e.target.value)}
                  placeholder="Ex: Restaurante"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="marcTipoGasto">Tipo de Gasto</Label>
                <Input
                  id="marcTipoGasto"
                  value={marcacaoTipoGasto}
                  onChange={(e) => setMarcacaoTipoGasto(e.target.value)}
                  placeholder="Ex: Ajustável - Lazer"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setMarcacaoModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveMarcacao}>
                {editingMarcacao ? 'Salvar' : 'Adicionar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
