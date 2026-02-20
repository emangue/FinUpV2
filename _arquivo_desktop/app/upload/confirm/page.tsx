"use client"

import * as React from "react"
import { Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import DashboardLayout from "@/components/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Edit, 
  Save,
  ArrowLeft,
  Download
} from "lucide-react"

interface PreviewTransaction {
  id: string
  tempId: number
  Data: string
  Estabelecimento: string
  Valor: number
  ValorPositivo: number
  TipoTransacao: string
  TipoGasto: string
  GRUPO: string
  SUBGRUPO: string
  IdParcela?: string
  banco_origem: string
  tipodocumento: string
  origem_classificacao: string
  ValidarIA: string
  MarcacaoIA: string
  isDuplicate: boolean
  hasIssue: boolean
  issueDescription?: string
  selected: boolean
}

interface UploadSession {
  sessionId: string
  fileName: string
  bank: string
  uploadDate: string
  totalTransactions: number
  transactionsPreview: PreviewTransaction[]
  duplicatesFound: number
  issuesFound: number
}

export default function ConfirmarUploadPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Carregando...</div>}>
      <ConfirmarUploadPageContent />
    </Suspense>
  )
}

function ConfirmarUploadPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const sessionId = searchParams.get('session')

  const [uploadSession, setUploadSession] = React.useState<UploadSession | null>(null)
  const [transactions, setTransactions] = React.useState<PreviewTransaction[]>([])
  const [loading, setLoading] = React.useState(true)
  const [saving, setSaving] = React.useState(false)
  
  // Estados para edição
  const [editModalOpen, setEditModalOpen] = React.useState(false)
  const [editingTransaction, setEditingTransaction] = React.useState<PreviewTransaction | null>(null)
  const [editForm, setEditForm] = React.useState({
    TipoGasto: '',
    GRUPO: '',
    SUBGRUPO: '',
    Estabelecimento: ''
  })

  // Estados de filtro
  const [showDuplicates, setShowDuplicates] = React.useState(false)
  const [showIssues, setShowIssues] = React.useState(false)
  const [showAll, setShowAll] = React.useState(true)

  React.useEffect(() => {
    if (!sessionId) {
      router.push('/upload')
      return
    }
    fetchUploadSession()
  }, [sessionId])

  const fetchUploadSession = async () => {
    try {
      setLoading(true)
      // TODO: Substituir por chamada real ao backend
      const mockData: UploadSession = {
        sessionId: sessionId!,
        fileName: 'fatura_itau_202512.csv',
        bank: 'Banco Itaú',
        uploadDate: new Date().toISOString(),
        totalTransactions: 45,
        transactionsPreview: generateMockTransactions(45),
        duplicatesFound: 3,
        issuesFound: 2
      }
      
      setUploadSession(mockData)
      setTransactions(mockData.transactionsPreview)
    } catch (error) {
      console.error('Erro ao buscar sessão de upload:', error)
    } finally {
      setLoading(false)
    }
  }

  const generateMockTransactions = (count: number): PreviewTransaction[] => {
    const estabelecimentos = ['MERCADO LIVRE', 'AMAZON BRASIL', 'IFOOD', 'UBER', 'NETFLIX', 'SPOTIFY', 'POSTO SHELL']
    const tipos = ['Cartão de Crédito', 'Despesas']
    const grupos = ['Alimentação', 'Transporte', 'Entretenimento', 'Compras Online']
    
    return Array.from({ length: count }, (_, i) => ({
      id: `temp_${i}`,
      tempId: i + 1,
      Data: `${String(Math.floor(Math.random() * 28) + 1).padStart(2, '0')}/12/2025`,
      Estabelecimento: estabelecimentos[Math.floor(Math.random() * estabelecimentos.length)],
      Valor: -(Math.random() * 500 + 10),
      ValorPositivo: Math.random() * 500 + 10,
      TipoTransacao: tipos[Math.floor(Math.random() * tipos.length)],
      TipoGasto: grupos[Math.floor(Math.random() * grupos.length)],
      GRUPO: grupos[Math.floor(Math.random() * grupos.length)],
      SUBGRUPO: 'Padrão',
      banco_origem: 'Itaú',
      tipodocumento: 'Fatura Cartão de Crédito',
      origem_classificacao: 'IA',
      ValidarIA: Math.random() > 0.5 ? 'Sim' : 'Não',
      MarcacaoIA: 'Automática',
      isDuplicate: i < 3, // Primeiras 3 são duplicadas
      hasIssue: i >= 3 && i < 5, // 2 tem problemas
      issueDescription: i >= 3 && i < 5 ? 'Estabelecimento não reconhecido' : undefined,
      selected: !(i < 3) // Duplicatas desmarcadas por padrão
    }))
  }

  const handleToggleTransaction = (tempId: number) => {
    setTransactions(prev =>
      prev.map(t => t.tempId === tempId ? { ...t, selected: !t.selected } : t)
    )
  }

  const handleToggleAll = () => {
    const allSelected = filteredTransactions.every(t => t.selected)
    setTransactions(prev =>
      prev.map(t => {
        if (shouldShowTransaction(t)) {
          return { ...t, selected: !allSelected }
        }
        return t
      })
    )
  }

  const handleEditTransaction = (transaction: PreviewTransaction) => {
    setEditingTransaction(transaction)
    setEditForm({
      TipoGasto: transaction.TipoGasto,
      GRUPO: transaction.GRUPO,
      SUBGRUPO: transaction.SUBGRUPO,
      Estabelecimento: transaction.Estabelecimento
    })
    setEditModalOpen(true)
  }

  const handleSaveEdit = () => {
    if (!editingTransaction) return

    setTransactions(prev =>
      prev.map(t =>
        t.tempId === editingTransaction.tempId
          ? {
              ...t,
              ...editForm,
              MarcacaoIA: 'Manual (Lote)',
              ValidarIA: 'Não'
            }
          : t
      )
    )
    setEditModalOpen(false)
    setEditingTransaction(null)
  }

  const handleSaveTransactions = async () => {
    const selectedTransactions = transactions.filter(t => t.selected)
    
    if (selectedTransactions.length === 0) {
      alert('Selecione pelo menos uma transação para salvar')
      return
    }

    if (!confirm(`Confirma o salvamento de ${selectedTransactions.length} transações?`)) {
      return
    }

    try {
      setSaving(true)
      
      // TODO: Implementar chamada ao backend
      // await uploadAPI.confirmAndSave(sessionId, selectedTransactions)
      
      console.log('Salvando transações:', selectedTransactions)
      
      // Simular delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      alert('Transações salvas com sucesso!')
      router.push('/transactions')
    } catch (error) {
      console.error('Erro ao salvar transações:', error)
      alert('Erro ao salvar transações. Tente novamente.')
    } finally {
      setSaving(false)
    }
  }

  const handleExportPreview = () => {
    const csv = [
      ['Data', 'Estabelecimento', 'Valor', 'Tipo', 'Grupo', 'Subgrupo', 'Status'],
      ...filteredTransactions.map(t => [
        t.Data,
        t.Estabelecimento,
        t.ValorPositivo.toFixed(2),
        t.TipoTransacao,
        t.GRUPO,
        t.SUBGRUPO,
        t.isDuplicate ? 'DUPLICATA' : t.hasIssue ? 'PROBLEMA' : 'OK'
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `preview_${uploadSession?.fileName || 'transacoes'}.csv`
    a.click()
  }

  const shouldShowTransaction = (t: PreviewTransaction) => {
    if (showAll) return true
    if (showDuplicates && t.isDuplicate) return true
    if (showIssues && t.hasIssue) return true
    return false
  }

  const filteredTransactions = transactions.filter(shouldShowTransaction)
  const selectedCount = filteredTransactions.filter(t => t.selected).length

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando preview...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!uploadSession) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <XCircle className="h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Sessão não encontrada</h2>
          <p className="text-gray-600 mb-4">A sessão de upload expirou ou não existe</p>
          <Button onClick={() => router.push('/upload')}>
            Voltar para Upload
          </Button>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push('/upload')}
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Voltar
              </Button>
            </div>
            <h1 className="text-3xl font-bold">Confirmar Upload</h1>
            <p className="text-gray-600 mt-1">
              Revise e valide as transações antes de salvar
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleExportPreview}>
              <Download className="h-4 w-4 mr-2" />
              Exportar Preview
            </Button>
            <Button 
              onClick={handleSaveTransactions}
              disabled={saving || selectedCount === 0}
              className="bg-green-600 hover:bg-green-700"
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? 'Salvando...' : `Salvar ${selectedCount} Transações`}
            </Button>
          </div>
        </div>

        {/* Info Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Arquivo</CardDescription>
              <CardTitle className="text-lg">{uploadSession.fileName}</CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Total de Transações</CardDescription>
              <CardTitle className="text-2xl">{uploadSession.totalTransactions}</CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Duplicatas Encontradas</CardDescription>
              <CardTitle className="text-2xl text-yellow-600">
                {uploadSession.duplicatesFound}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardDescription>Problemas Detectados</CardDescription>
              <CardTitle className="text-2xl text-red-600">
                {uploadSession.issuesFound}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Filtros de Visualização</CardTitle>
                <CardDescription>
                  {selectedCount} de {filteredTransactions.length} transações selecionadas
                </CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={handleToggleAll}>
                {filteredTransactions.every(t => t.selected) ? 'Desmarcar Todas' : 'Marcar Todas'}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Button
                variant={showAll ? 'default' : 'outline'}
                onClick={() => {
                  setShowAll(true)
                  setShowDuplicates(false)
                  setShowIssues(false)
                }}
              >
                Todas ({transactions.length})
              </Button>
              <Button
                variant={showDuplicates ? 'default' : 'outline'}
                onClick={() => {
                  setShowAll(false)
                  setShowDuplicates(true)
                  setShowIssues(false)
                }}
              >
                Duplicatas ({uploadSession.duplicatesFound})
              </Button>
              <Button
                variant={showIssues ? 'default' : 'outline'}
                onClick={() => {
                  setShowAll(false)
                  setShowDuplicates(false)
                  setShowIssues(true)
                }}
              >
                Problemas ({uploadSession.issuesFound})
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Transactions Table */}
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[50px]">
                      <Checkbox
                        checked={filteredTransactions.every(t => t.selected)}
                        onCheckedChange={handleToggleAll}
                      />
                    </TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Estabelecimento</TableHead>
                    <TableHead>Valor</TableHead>
                    <TableHead>Tipo</TableHead>
                    <TableHead>Grupo</TableHead>
                    <TableHead>Subgrupo</TableHead>
                    <TableHead>Marcação</TableHead>
                    <TableHead className="w-[100px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTransactions.map((transaction) => (
                    <TableRow 
                      key={transaction.tempId}
                      className={
                        transaction.isDuplicate ? 'bg-yellow-50' :
                        transaction.hasIssue ? 'bg-red-50' :
                        ''
                      }
                    >
                      <TableCell>
                        <Checkbox
                          checked={transaction.selected}
                          onCheckedChange={() => handleToggleTransaction(transaction.tempId)}
                        />
                      </TableCell>
                      <TableCell>
                        {transaction.isDuplicate ? (
                          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                            Duplicata
                          </Badge>
                        ) : transaction.hasIssue ? (
                          <Badge variant="destructive">
                            Problema
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="bg-green-100 text-green-800">
                            OK
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>{transaction.Data}</TableCell>
                      <TableCell className="font-medium">{transaction.Estabelecimento}</TableCell>
                      <TableCell className="font-mono">
                        {formatCurrency(transaction.ValorPositivo)}
                      </TableCell>
                      <TableCell>{transaction.TipoTransacao}</TableCell>
                      <TableCell>{transaction.GRUPO}</TableCell>
                      <TableCell>{transaction.SUBGRUPO}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {transaction.MarcacaoIA}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleEditTransaction(transaction)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Edit Modal */}
        <Dialog open={editModalOpen} onOpenChange={setEditModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Editar Transação</DialogTitle>
              <DialogDescription>
                Ajuste a classificação manualmente
              </DialogDescription>
            </DialogHeader>
            
            {editingTransaction && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="estabelecimento">Estabelecimento</Label>
                  <Input
                    id="estabelecimento"
                    value={editForm.Estabelecimento}
                    onChange={(e) => setEditForm(prev => ({ ...prev, Estabelecimento: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="tipoGasto">Tipo de Gasto</Label>
                  <Input
                    id="tipoGasto"
                    value={editForm.TipoGasto}
                    onChange={(e) => setEditForm(prev => ({ ...prev, TipoGasto: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="grupo">Grupo</Label>
                  <Input
                    id="grupo"
                    value={editForm.GRUPO}
                    onChange={(e) => setEditForm(prev => ({ ...prev, GRUPO: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="subgrupo">Subgrupo</Label>
                  <Input
                    id="subgrupo"
                    value={editForm.SUBGRUPO}
                    onChange={(e) => setEditForm(prev => ({ ...prev, SUBGRUPO: e.target.value }))}
                  />
                </div>

                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-900">
                    <strong>Dados originais:</strong>
                  </p>
                  <p className="text-sm text-blue-700">
                    {editingTransaction.Data} • {formatCurrency(editingTransaction.ValorPositivo)}
                  </p>
                </div>
              </div>
            )}

            <DialogFooter>
              <Button variant="outline" onClick={() => setEditModalOpen(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSaveEdit}>
                Salvar Alterações
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
