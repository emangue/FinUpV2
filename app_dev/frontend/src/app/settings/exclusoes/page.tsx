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
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, CheckCircle2 } from "lucide-react"
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

interface Exclusao {
  id: number
  nome_transacao: string
  banco: string | null
  tipo_documento: string | null
  descricao: string | null
  ativo: number
  acao: string // 'EXCLUIR' ou 'IGNORAR'
}

interface BankCompatibility {
  id: number
  bank_name: string
  file_format: string
  status: 'OK' | 'WIP' | 'TBD'
}

export default function ExclusoesPage() {
  const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` : "http://localhost:8000/api/v1"
  const [exclusoes, setExclusoes] = React.useState<Exclusao[]>([])
  const [loadingExclusoes, setLoadingExclusoes] = React.useState(true)
  const [exclusaoModalOpen, setExclusaoModalOpen] = React.useState(false)
  const [exclusaoNome, setExclusaoNome] = React.useState('')
  const [exclusaoBanco, setExclusaoBanco] = React.useState('')
  const [exclusaoTipoCartao, setExclusaoTipoCartao] = React.useState(false)
  const [exclusaoTipoExtrato, setExclusaoTipoExtrato] = React.useState(false)
  const [exclusaoDescricao, setExclusaoDescricao] = React.useState('')
  const [exclusaoAcao, setExclusaoAcao] = React.useState('EXCLUIR')
  const [editingExclusao, setEditingExclusao] = React.useState<Exclusao | null>(null)
  const [bancos, setBancos] = React.useState<BankCompatibility[]>([])
  const [notification, setNotification] = React.useState<{ type: 'success' | 'error', message: string } | null>(null)

  React.useEffect(() => {
    fetchExclusoes()
    fetchBancos()
  }, [])

  const fetchExclusoes = async () => {
    try {
      setLoadingExclusoes(true)
      const response = await fetch('/api/exclusoes')
      if (response.ok) {
        const data = await response.json()
        console.log('Exclusões recebidas:', data)
        setExclusoes(data.exclusoes || [])
      } else {
        console.error('Erro ao buscar exclusões:', response.status)
        setNotification({ type: 'error', message: `Erro ao buscar exclusões (${response.status})` })
      }
    } catch (error) {
      console.error('Erro ao buscar exclusões:', error)
      setNotification({ type: 'error', message: 'Erro ao carregar exclusões' })
    } finally {
      setLoadingExclusoes(false)
    }
  }

  const fetchBancos = async () => {
    try {
      const response = await fetch('/api/compatibility')
      if (response.ok) {
        const data = await response.json()
        console.log('Bancos recebidos:', data)
        // API retorna { banks: [...], total: N }
        setBancos(data.banks || [])
      } else {
        console.error('Erro ao buscar bancos:', response.status)
        setNotification({ type: 'error', message: `Erro ao buscar bancos (${response.status})` })
      }
    } catch (error) {
      console.error('Erro ao buscar bancos:', error)
      setNotification({ type: 'error', message: 'Erro ao conectar com servidor' })
    }
  }

  const uniqueBanks = [...new Set(bancos.map(b => b.bank_name))]

  const handleAddExclusao = () => {
    setExclusaoNome('')
    setExclusaoBanco('TODOS')
    setExclusaoTipoCartao(true)
    setExclusaoTipoExtrato(true)
    setExclusaoDescricao('')
    setExclusaoAcao('EXCLUIR')
    setEditingExclusao(null)
    setExclusaoModalOpen(true)
  }

  const handleEditExclusao = (exclusao: Exclusao) => {
    console.log('Editando exclusão:', exclusao)
    console.log('ID da exclusão:', exclusao.id)
    setEditingExclusao(exclusao)
    setExclusaoNome(exclusao.nome_transacao)
    setExclusaoBanco(exclusao.banco || 'TODOS')
    
    // Determinar checkboxes baseado no tipo_documento
    const tipo = exclusao.tipo_documento || 'ambos'
    setExclusaoTipoCartao(tipo === 'cartao' || tipo === 'ambos')
    setExclusaoTipoExtrato(tipo === 'extrato' || tipo === 'ambos')
    
    setExclusaoDescricao(exclusao.descricao || '')
    setExclusaoAcao(exclusao.acao || 'EXCLUIR')
    setExclusaoModalOpen(true)
  }

  const handleSaveExclusao = async () => {
    console.log('Salvando exclusão. Modo edição:', !!editingExclusao)
    console.log('editingExclusao:', editingExclusao)
    
    if (!exclusaoNome.trim()) {
      setNotification({ type: 'error', message: 'Nome da transação é obrigatório' })
      return
    }

    if (!exclusaoTipoCartao && !exclusaoTipoExtrato) {
      setNotification({ type: 'error', message: 'Selecione pelo menos um tipo de documento' })
      return
    }

    // Determinar tipo_documento baseado nos checkboxes
    let tipoDocumento = 'ambos'
    if (exclusaoTipoCartao && !exclusaoTipoExtrato) {
      tipoDocumento = 'cartao'
    } else if (exclusaoTipoExtrato && !exclusaoTipoCartao) {
      tipoDocumento = 'extrato'
    }

    try {
      const url = editingExclusao && editingExclusao.id 
        ? `/api/exclusoes/${editingExclusao.id}` 
        : '/api/exclusoes'
      const method = editingExclusao && editingExclusao.id ? 'PUT' : 'POST'
      
      console.log('URL:', url)
      console.log('Method:', method)
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nome_transacao: exclusaoNome.trim(),
          banco: exclusaoBanco === 'TODOS' ? null : exclusaoBanco.trim(),
          tipo_documento: tipoDocumento,
          descricao: exclusaoDescricao.trim() || null,
          acao: exclusaoAcao
        })
      })

      if (response.ok) {
        setNotification({ type: 'success', message: `Regra ${editingExclusao ? 'atualizada' : 'adicionada'} com sucesso!` })
        fetchExclusoes()
        setTimeout(() => {
          setExclusaoModalOpen(false)
          setNotification(null)
        }, 1500)
      } else {
        try {
          const errorData = await response.json()
          console.error('Erro do servidor:', errorData)
          let errorMsg = 'Erro desconhecido'
          if (typeof errorData === 'string') {
            errorMsg = errorData
          } else if (errorData.detail) {
            errorMsg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail)
          } else if (errorData.error) {
            errorMsg = errorData.error
          } else if (errorData.message) {
            errorMsg = errorData.message
          } else {
            errorMsg = JSON.stringify(errorData)
          }
          setNotification({ type: 'error', message: `Erro ao salvar: ${errorMsg}` })
        } catch (parseError) {
          setNotification({ type: 'error', message: `Erro ao salvar (Status ${response.status})` })
        }
      }
    } catch (error) {
      console.error('Erro ao salvar exclusão:', error)
      const errorMsg = error instanceof Error ? error.message : String(error)
      setNotification({ type: 'error', message: `Erro ao salvar: ${errorMsg}` })
    }
  }

  const handleAcaoChange = async (id: number, novaAcao: string) => {
    try {
      const exclusao = exclusoes.find(e => e.id === id)
      if (!exclusao) return

      const response = await fetch(`${apiUrl}/exclusoes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...exclusao,
          acao: novaAcao
        })
      })

      if (response.ok) {
        setNotification({ type: 'success', message: 'Ação atualizada com sucesso!' })
        fetchExclusoes()
        setTimeout(() => setNotification(null), 2000)
      } else {
        setNotification({ type: 'error', message: 'Erro ao atualizar ação' })
      }
    } catch (error) {
      console.error('Erro ao atualizar ação:', error)
      setNotification({ type: 'error', message: 'Erro ao atualizar ação' })
    }
  }

  const handleDeleteExclusao = async (id: number) => {
    if (!confirm('Deseja realmente deletar esta regra?')) return

    try {
      const response = await fetch(`${apiUrl}/exclusoes/${id}`, {
        method: 'DELETE'
      })

      if (response.ok) {
        setNotification({ type: 'success', message: 'Regra excluída com sucesso!' })
        fetchExclusoes()
        setTimeout(() => setNotification(null), 2000)
      } else {
        setNotification({ type: 'error', message: 'Erro ao deletar regra' })
      }
    } catch (error) {
      console.error('Erro ao deletar exclusão:', error)
      setNotification({ type: 'error', message: 'Erro ao deletar regra' })
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        {notification && (
          <Alert variant={notification.type === 'error' ? 'destructive' : 'default'} className="mb-4">
            {notification.type === 'error' ? (
              <AlertCircle className="h-4 w-4" />
            ) : (
              <CheckCircle2 className="h-4 w-4" />
            )}
            <AlertTitle>{notification.type === 'error' ? 'Erro' : 'Sucesso'}</AlertTitle>
            <AlertDescription>{notification.message}</AlertDescription>
          </Alert>
        )}
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Excluir / Ignorar</h1>
            <p className="text-muted-foreground">
              Gerencie transações que devem ser excluídas ou ignoradas durante a importação
            </p>
          </div>
        </div>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Transações a Excluir / Ignorar</CardTitle>
              <CardDescription>
                {exclusoes.length} regras cadastradas ({exclusoes.filter(e => e.acao === 'EXCLUIR').length} excluir, {exclusoes.filter(e => e.acao === 'IGNORAR').length} ignorar)
              </CardDescription>
            </div>
            <Button onClick={handleAddExclusao}>
              <Plus className="mr-2 h-4 w-4" />
              Nova Regra
            </Button>
          </CardHeader>
          <CardContent>
            {loadingExclusoes ? (
              <div className="flex items-center justify-center py-8 text-muted-foreground">
                Carregando exclusões...
              </div>
            ) : exclusoes.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <p>Nenhuma regra cadastrada</p>
                <p className="text-sm mt-1">Clique em "Nova Regra" para adicionar</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Nome da Transação</TableHead>
                    <TableHead>Banco</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Ação</TableHead>
                    <TableHead>Descrição</TableHead>
                    <TableHead className="w-[100px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {exclusoes.map((exclusao) => (
                  <TableRow key={exclusao.id}>
                    <TableCell className="font-medium">{exclusao.nome_transacao}</TableCell>
                    <TableCell>{exclusao.banco || <span className="text-muted-foreground">Todos</span>}</TableCell>
                    <TableCell>
                      <span className="text-sm">
                        {exclusao.tipo_documento === 'cartao' ? 'Cartão' :
                         exclusao.tipo_documento === 'extrato' ? 'Extrato' :
                         'Ambos'}
                      </span>
                    </TableCell>
                    <TableCell>
                      <Select
                        value={exclusao.acao || 'EXCLUIR'}
                        onValueChange={(value) => handleAcaoChange(exclusao.id, value)}
                      >
                        <SelectTrigger className="w-[130px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="EXCLUIR">
                            <span className="flex items-center gap-2">
                              <span className="h-2 w-2 rounded-full bg-red-500"></span>
                              Excluir
                            </span>
                          </SelectItem>
                          <SelectItem value="IGNORAR">
                            <span className="flex items-center gap-2">
                              <span className="h-2 w-2 rounded-full bg-yellow-500"></span>
                              Ignorar
                            </span>
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {exclusao.descricao || '-'}
                    </TableCell>
                    <TableCell className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleEditExclusao(exclusao)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeleteExclusao(exclusao.id)}
                      >
                        <X className="h-4 w-4 text-red-600" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            )}
          </CardContent>
        </Card>

        <Dialog open={exclusaoModalOpen} onOpenChange={setExclusaoModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>
                {editingExclusao ? 'Editar' : 'Adicionar'} Regra
              </DialogTitle>
              <DialogDescription>
                {editingExclusao ? 'Altere' : 'Insira'} o nome da transação a ser excluída ou ignorada
              </DialogDescription>
            </DialogHeader>
            
            {notification && (
              <Alert variant={notification.type === 'error' ? 'destructive' : 'default'} className="mb-2">
                {notification.type === 'error' ? (
                  <AlertCircle className="h-4 w-4" />
                ) : (
                  <CheckCircle2 className="h-4 w-4" />
                )}
                <AlertTitle>{notification.type === 'error' ? 'Erro' : 'Sucesso'}</AlertTitle>
                <AlertDescription>{notification.message}</AlertDescription>
              </Alert>
            )}
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="exclusaoNome">Nome da Transação</Label>
                <Input
                  id="exclusaoNome"
                  value={exclusaoNome}
                  onChange={(e) => setExclusaoNome(e.target.value)}
                  placeholder="Ex: PAGAMENTO EFETUADO"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="exclusaoBanco">Banco (opcional)</Label>
                <Select value={exclusaoBanco || 'TODOS'} onValueChange={(value) => setExclusaoBanco(value === 'TODOS' ? '' : value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Todos os bancos" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="TODOS">Todos os bancos</SelectItem>
                    {uniqueBanks.map((banco) => (
                      <SelectItem key={banco} value={banco}>
                        {banco}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Aplicar exclusão para</Label>
                <div className="flex flex-col space-y-2">
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="tipo-cartao"
                      checked={exclusaoTipoCartao}
                      onChange={(e) => setExclusaoTipoCartao(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="tipo-cartao" className="font-normal cursor-pointer">
                      Cartão de Crédito
                    </Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="tipo-extrato"
                      checked={exclusaoTipoExtrato}
                      onChange={(e) => setExclusaoTipoExtrato(e.target.checked)}
                      className="w-4 h-4"
                    />
                    <Label htmlFor="tipo-extrato" className="font-normal cursor-pointer">
                      Extrato Bancário
                    </Label>
                  </div>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="exclusaoAcao">Ação</Label>
                <Select value={exclusaoAcao} onValueChange={setExclusaoAcao}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EXCLUIR">
                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-red-500"></span>
                        <div>
                          <div className="font-medium">Excluir</div>
                          <div className="text-xs text-muted-foreground">Remove da importação (não aparece no preview)</div>
                        </div>
                      </div>
                    </SelectItem>
                    <SelectItem value="IGNORAR">
                      <div className="flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-yellow-500"></span>
                        <div>
                          <div className="font-medium">Ignorar</div>
                          <div className="text-xs text-muted-foreground">Importa mas não conta em dashboards</div>
                        </div>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="exclusaoDescricao">Descrição (opcional)</Label>
                <Input
                  id="exclusaoDescricao"
                  value={exclusaoDescricao}
                  onChange={(e) => setExclusaoDescricao(e.target.value)}
                  placeholder="Ex: Pagamento da fatura anterior"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setExclusaoModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveExclusao}>
                {editingExclusao ? 'Salvar' : 'Adicionar'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
