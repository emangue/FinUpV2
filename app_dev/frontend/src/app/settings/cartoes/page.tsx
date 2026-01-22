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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
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
import { Plus, Edit, X } from "lucide-react"

interface Cartao {
  id: number
  nome_cartao: string
  final_cartao: string
  banco: string
  ativo: number
}

interface BankCompatibility {
  id: number
  bank_name: string
  file_format: string
  status: 'OK' | 'WIP' | 'TBD'
}

export default function CartoesPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"
  const [cartoes, setCartoes] = React.useState<Cartao[]>([])
  const [loadingCartoes, setLoadingCartoes] = React.useState(true)
  const [cartaoModalOpen, setCartaoModalOpen] = React.useState(false)
  const [cartaoNome, setCartaoNome] = React.useState('')
  const [cartaoFinal, setCartaoFinal] = React.useState('')
  const [cartaoBanco, setCartaoBanco] = React.useState('')
  const [editingCartao, setEditingCartao] = React.useState<Cartao | null>(null)
  const [bancos, setBancos] = React.useState<BankCompatibility[]>([])

  React.useEffect(() => {
    fetchCartoes()
    fetchBancos()
  }, [])

  const fetchCartoes = async () => {
    try {
      setLoadingCartoes(true)
      const response = await fetch('/api/cards')
      if (response.ok) {
        const data = await response.json()
        setCartoes(data.cards || [])
      }
    } catch (error) {
      console.error('Erro ao buscar cartões:', error)
    } finally {
      setLoadingCartoes(false)
    }
  }

  const fetchBancos = async () => {
    try {
      const response = await fetch('/api/compatibility/manage')
      if (response.ok) {
        const data = await response.json()
        setBancos(data)
      }
    } catch (error) {
      console.error('Erro ao buscar bancos:', error)
    }
  }

  const uniqueBanks = [...new Set(bancos.map(b => b.bank_name))]

  const handleAddCartao = () => {
    setCartaoNome('')
    setCartaoFinal('')
    setCartaoBanco('')
    setEditingCartao(null)
    setCartaoModalOpen(true)
  }

  const handleEditCartao = (cartao: Cartao) => {
    console.log('Editando cartão:', cartao)
    console.log('ID do cartão:', cartao.id)
    setEditingCartao(cartao)
    setCartaoNome(cartao.nome_cartao)
    setCartaoFinal(cartao.final_cartao)
    setCartaoBanco(cartao.banco)
    setCartaoModalOpen(true)
  }

  const handleSaveCartao = async () => {
    console.log('Salvando cartão. Modo edição:', !!editingCartao)
    console.log('editingCartao:', editingCartao)
    
    if (!cartaoNome.trim() || !cartaoFinal.trim() || !cartaoBanco.trim()) {
      alert('Todos os campos são obrigatórios')
      return
    }

    if (cartaoFinal.length !== 4 || !/^\d+$/.test(cartaoFinal)) {
      alert('Final do cartão deve ter exatamente 4 dígitos')
      return
    }

    try {
      const url = editingCartao && editingCartao.id 
        ? `/api/cartoes/${editingCartao.id}` 
        : '/api/cartoes'
      const method = editingCartao && editingCartao.id ? 'PUT' : 'POST'
      
      console.log('URL:', url)
      console.log('Method:', method)
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome_cartao: cartaoNome.trim(),
          final_cartao: cartaoFinal.trim(),
          banco: cartaoBanco.trim()
        })
      })

      if (response.ok) {
        fetchCartoes()
        setCartaoModalOpen(false)
      } else {
        try {
          const errorData = await response.json()
          console.error('Erro do servidor:', errorData)
          let errorMsg = 'Erro desconhecido'
          if (typeof errorData === 'string') {
            errorMsg = errorData
          } else if (errorData.detail) {
            errorMsg = errorData.detail
          } else if (errorData.error) {
            errorMsg = errorData.error
          } else if (errorData.message) {
            errorMsg = errorData.message
          } else {
            errorMsg = JSON.stringify(errorData)
          }
          alert(`Erro ao salvar: ${errorMsg}`)
        } catch (parseError) {
          alert(`Erro ao salvar (Status ${response.status})`)
        }
      }
    } catch (error) {
      console.error('Erro ao salvar cartão:', error)
      const errorMsg = error instanceof Error ? error.message : String(error)
      alert(`Erro ao salvar cartão: ${errorMsg}`)
    }
  }

  const handleDeleteCartao = async (id: number) => {
    if (!confirm('Deseja realmente deletar este cartão?')) return

    try {
      const response = await fetch(`${apiUrl}/cartoes/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        fetchCartoes()
      }
    } catch (error) {
      console.error('Erro ao deletar cartão:', error)
      alert('Erro ao deletar cartão')
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Cartões</h1>
            <p className="text-muted-foreground">
              Gerencie seus cartões de crédito cadastrados
            </p>
          </div>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Cartões de Crédito</CardTitle>
              <CardDescription>
                {cartoes.length} cartões cadastrados
              </CardDescription>
            </div>
            <Button onClick={handleAddCartao}>
              <Plus className="mr-2 h-4 w-4" />
              Novo Cartão
            </Button>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Final</TableHead>
                  <TableHead>Banco</TableHead>
                  <TableHead className="w-[100px]">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {cartoes.map((cartao) => (
                  <TableRow key={cartao.id}>
                    <TableCell className="font-medium">{cartao.nome_cartao}</TableCell>
                    <TableCell>•••• {cartao.final_cartao}</TableCell>
                    <TableCell>{cartao.banco}</TableCell>
                    <TableCell className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditCartao(cartao)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteCartao(cartao.id)}
                      >
                        <X className="h-4 w-4 text-red-600" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Dialog open={cartaoModalOpen} onOpenChange={setCartaoModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingCartao ? 'Editar' : 'Adicionar'} Cartão
              </DialogTitle>
              <DialogDescription>
                {editingCartao ? 'Altere' : 'Insira'} os dados do cartão de crédito
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cartaoNome">Nome do Cartão</Label>
                <Input
                  id="cartaoNome"
                  value={cartaoNome}
                  onChange={(e) => setCartaoNome(e.target.value)}
                  placeholder="Ex: Mastercard Black"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cartaoFinal">Final do Cartão (4 dígitos)</Label>
                <Input
                  id="cartaoFinal"
                  value={cartaoFinal}
                  onChange={(e) => setCartaoFinal(e.target.value.replace(/\D/g, '').slice(0, 4))}
                  placeholder="1234"
                  maxLength={4}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cartaoBanco">Banco Emissor</Label>
                <Select value={cartaoBanco} onValueChange={setCartaoBanco}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o banco" />
                  </SelectTrigger>
                  <SelectContent>
                    {uniqueBanks.map((banco) => (
                      <SelectItem key={banco} value={banco}>
                        {banco}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCartaoModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveCartao}>
                {editingCartao ? 'Salvar' : 'Adicionar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
