"use client"

import * as React from "react"
import { Suspense } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { toast } from 'sonner'
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
import { Checkbox } from "@/components/ui/checkbox"
import { 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Edit, 
  Save,
  ArrowLeft,
  Download,
  AlertTriangle,
  Copy
} from "lucide-react"

interface Transaction {
  id: string
  tempId: number
  data: string
  estabelecimento: string
  valor: number
  valorPositivo: number
  tipoTransacao: string
  tipoGasto: string
  grupo: string
  subgrupo: string
  idParcela?: string
  banco_origem: string
  tipodocumento: string
  origem_classificacao: string
  categoriaGeral: string
  classified: boolean
  selected: boolean
  duplicateInfo?: {
    isDuplicate: boolean
    isExactDuplicate: boolean
    similarity: number
    existing?: any
  }
}

interface ClassificationSummary {
  total: number
  classified: number
  duplicates: number
  exactDuplicates: number
}

export default function UploadConfirmPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Carregando...</div>}>
      <UploadConfirmPageContent />
    </Suspense>
  )
}

function UploadConfirmPageContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const fileParam = searchParams.get('file')
  
  const [file, setFile] = React.useState<File | null>(null)
  const [transactions, setTransactions] = React.useState<Transaction[]>([])
  const [summary, setSummary] = React.useState<ClassificationSummary | null>(null)
  const [isProcessing, setIsProcessing] = React.useState(false)
  const [isConfirming, setIsConfirming] = React.useState(false)
  const [error, setError] = React.useState('')
  const [showConfirmDialog, setShowConfirmDialog] = React.useState(false)
  
  // Estados para edição
  const [editModalOpen, setEditModalOpen] = React.useState(false)
  const [editingTransaction, setEditingTransaction] = React.useState<Transaction | null>(null)
  const [editForm, setEditForm] = React.useState({
    tipoGasto: '',
    grupo: '',
    subgrupo: '',
    estabelecimento: ''
  })

  // Estados de filtro
  const [showDuplicates, setShowDuplicates] = React.useState(false)
  const [showUnclassified, setShowUnclassified] = React.useState(false)
  const [showAll, setShowAll] = React.useState(true)

  React.useEffect(() => {
    // Recuperar arquivo da sessão
    const uploadFileInfo = sessionStorage.getItem('uploadFile')
    const uploadFileData = sessionStorage.getItem('uploadFileData')
    
    if (!uploadFileInfo || !uploadFileData) {
      router.push('/upload')
      return
    }
    
    try {
      const fileInfo = JSON.parse(uploadFileInfo)
      
      // Recriar o arquivo a partir dos dados armazenados
      const byteCharacters = atob(uploadFileData.split(',')[1])
      const byteNumbers = new Array(byteCharacters.length)
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      const byteArray = new Uint8Array(byteNumbers)
      const reconstructedFile = new File([byteArray], fileInfo.name, { type: fileInfo.type })
      
      // Processar o arquivo automaticamente
      processFile(reconstructedFile)
      
    } catch (error) {
      console.error('Erro ao recuperar arquivo da sessão:', error)
      setError('Erro ao recuperar arquivo. Faça upload novamente.')
    }
  }, [])

  const processFile = async (uploadedFile: File) => {
    setIsProcessing(true)
    setError('')
    setFile(uploadedFile)

    try {
      // 1. Processar arquivo com Python
      const formData = new FormData()
      formData.append('file', uploadedFile)

      const processResponse = await fetch('/api/upload/process', {
        method: 'POST',
        body: formData,
      })

      if (!processResponse.ok) {
        const errorData = await processResponse.json()
        throw new Error(errorData.error || 'Erro no processamento')
      }

      const processData = await processResponse.json()
      console.log('Dados processados:', processData)
      
      // 2. Classificar transações com IA
      const classifyResponse = await fetch('/api/upload/classify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transactions: processData.transactions,
          sessionId: Date.now().toString()
        }),
      })

      if (!classifyResponse.ok) {
        const errorData = await classifyResponse.json()
        throw new Error(errorData.error || 'Erro na classificação')
      }

      const classifyData = await classifyResponse.json()
      console.log('Dados classificados:', classifyData)
      
      // 3. Combinar dados do processamento com classificação
      const enrichedTransactions = processData.transactions.map((transaction: any, index: number) => ({
        id: `temp_${index}`,
        tempId: index + 1,
        data: transaction.data,
        estabelecimento: transaction.estabelecimento,
        valor: transaction.valor,
        valorPositivo: transaction.valorPositivo,
        tipoTransacao: transaction.tipoTransacao,
        tipoGasto: classifyData.transactions[index]?.tipoGasto || transaction.tipoGasto,
        grupo: classifyData.transactions[index]?.grupo || transaction.grupo,
        subgrupo: classifyData.transactions[index]?.subgrupo || transaction.subgrupo,
        banco_origem: transaction.banco_origem,
        tipodocumento: transaction.tipodocumento,
        origem_classificacao: classifyData.transactions[index]?.origem_classificacao || 'Sem classificação',
        categoriaGeral: classifyData.transactions[index]?.categoriaGeral || 'Não classificado',
        classified: classifyData.transactions[index]?.classified || false,
        duplicateInfo: classifyData.duplicates[index],
        selected: !classifyData.duplicates[index]?.isDuplicate // Duplicatas desmarcadas por padrão
      }))

      setTransactions(enrichedTransactions)
      setSummary(classifyData.summary)

    } catch (error) {
      console.error('Erro no processamento:', error)
      setError('Erro ao processar arquivo: ' + (error as Error).message)
    } finally {
      setIsProcessing(false)
    }
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

  const handleEditTransaction = (transaction: Transaction) => {
    setEditingTransaction(transaction)
    setEditForm({
      tipoGasto: transaction.tipoGasto,
      grupo: transaction.grupo,
      subgrupo: transaction.subgrupo,
      estabelecimento: transaction.estabelecimento
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
              origem_classificacao: 'Manual (Edição)',
              classified: true
            }
          : t
      )
    )
    setEditModalOpen(false)
    setEditingTransaction(null)
  }

  const handleConfirmTransactions = () => {
    const selectedTransactions = transactions.filter(t => t.selected)
    
    if (selectedTransactions.length === 0) {
      toast.error('Selecione pelo menos uma transação para confirmar')
      return
    }

    setShowConfirmDialog(true)
  }

  const handleDoConfirm = async () => {
    setShowConfirmDialog(false)
    const selectedTransactions = transactions.filter(t => t.selected)

    try {
      setIsConfirming(true)
      
      const response = await fetch('/api/upload/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transactions: selectedTransactions.map(t => ({
            ...t,
            // Remover campos temporários
            id: undefined,
            tempId: undefined,
            selected: undefined,
            duplicateInfo: undefined
          })),
          metadata: {
            arquivo_origem: file?.name,
            total_transactions: selectedTransactions.length,
            classificacao_ia: summary?.classified,
            duplicates_found: summary?.duplicates
          }
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Erro ao confirmar transações')
      }

      const result = await response.json()
      console.log('Transações confirmadas:', result)
      
      toast.success(`${result.inserted} transações importadas com sucesso!`)
      router.push('/transactions')
      
    } catch (error) {
      console.error('Erro ao confirmar transações:', error)
      toast.error('Erro ao confirmar transações: ' + (error as Error).message)
    } finally {
      setIsConfirming(false)
    }
  }

  const handleExportPreview = () => {
    if (transactions.length === 0) return

    const csv = [
      ['Data', 'Estabelecimento', 'Valor', 'Tipo', 'Grupo', 'Subgrupo', 'Classificação', 'Status'],
      ...filteredTransactions.map(t => [
        t.data,
        t.estabelecimento,
        t.valorPositivo.toFixed(2),
        t.tipoTransacao,
        t.grupo,
        t.subgrupo,
        t.origem_classificacao,
        t.duplicateInfo?.isDuplicate ? 'DUPLICATA' : 
        !t.classified ? 'NÃO CLASSIFICADO' : 'OK'
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `preview_${file?.name || 'transacoes'}.csv`
    a.click()
  }

  const shouldShowTransaction = (t: Transaction) => {
    if (showAll) return true
    if (showDuplicates && t.duplicateInfo?.isDuplicate) return true
    if (showUnclassified && !t.classified) return true
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

  if (isProcessing) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-lg font-medium mb-2">Processando arquivo...</h3>
            <p className="text-gray-600">Analisando transações e aplicando classificação IA</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <XCircle className="h-16 w-16 text-red-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Erro no Processamento</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => router.push('/upload')}>
            Voltar para Upload
          </Button>
        </div>
      </DashboardLayout>
    )
  }

  if (transactions.length === 0) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <AlertTriangle className="h-16 w-16 text-yellow-500 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Nenhuma Transação Encontrada</h2>
          <p className="text-gray-600 mb-4">O arquivo não contém transações válidas</p>
          <Button onClick={() => router.push('/upload')}>
            Tentar Novo Arquivo
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
            <h1 className="text-3xl font-bold">Confirmar Importação</h1>
            <p className="text-gray-600 mt-1">
              Revise as transações classificadas e confirme a importação
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleExportPreview}>
              <Download className="h-4 w-4 mr-2" />
              Exportar Preview
            </Button>
            <Button 
              onClick={handleConfirmTransactions}
              disabled={isConfirming || selectedCount === 0}
              className="bg-green-600 hover:bg-green-700"
            >
              <Save className="h-4 w-4 mr-2" />
              {isConfirming ? 'Confirmando...' : `Confirmar ${selectedCount} Transações`}
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Total de Transações</CardDescription>
                <CardTitle className="text-2xl">{summary.total}</CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Classificadas por IA</CardDescription>
                <CardTitle className="text-2xl text-blue-600">
                  {summary.classified}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Duplicatas Encontradas</CardDescription>
                <CardTitle className="text-2xl text-yellow-600">
                  {summary.duplicates}
                </CardTitle>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>Duplicatas Exatas</CardDescription>
                <CardTitle className="text-2xl text-red-600">
                  {summary.exactDuplicates}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>
        )}

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
                  setShowUnclassified(false)
                }}
              >
                Todas ({transactions.length})
              </Button>
              <Button
                variant={showDuplicates ? 'default' : 'outline'}
                onClick={() => {
                  setShowAll(false)
                  setShowDuplicates(true)
                  setShowUnclassified(false)
                }}
              >
                Duplicatas ({summary?.duplicates || 0})
              </Button>
              <Button
                variant={showUnclassified ? 'default' : 'outline'}
                onClick={() => {
                  setShowAll(false)
                  setShowDuplicates(false)
                  setShowUnclassified(true)
                }}
              >
                Não Classificadas ({transactions.filter(t => !t.classified).length})
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
                        checked={filteredTransactions.length > 0 && filteredTransactions.every(t => t.selected)}
                        onCheckedChange={handleToggleAll}
                      />
                    </TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Data</TableHead>
                    <TableHead>Estabelecimento</TableHead>
                    <TableHead>Valor</TableHead>
                    <TableHead>Grupo</TableHead>
                    <TableHead>Subgrupo</TableHead>
                    <TableHead>Classificação</TableHead>
                    <TableHead>Similaridade</TableHead>
                    <TableHead className="w-[100px]">Ações</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredTransactions.map((transaction) => (
                    <TableRow 
                      key={transaction.tempId}
                      className={
                        transaction.duplicateInfo?.isExactDuplicate ? 'bg-red-50' :
                        transaction.duplicateInfo?.isDuplicate ? 'bg-yellow-50' :
                        !transaction.classified ? 'bg-blue-50' :
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
                        {transaction.duplicateInfo?.isExactDuplicate ? (
                          <Badge variant="destructive">
                            <Copy className="h-3 w-3 mr-1" />
                            Exata
                          </Badge>
                        ) : transaction.duplicateInfo?.isDuplicate ? (
                          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                            Duplicata
                          </Badge>
                        ) : !transaction.classified ? (
                          <Badge variant="outline">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            Não Classificado
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="bg-green-100 text-green-800">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            OK
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>{transaction.data}</TableCell>
                      <TableCell className="font-medium">{transaction.estabelecimento}</TableCell>
                      <TableCell className="font-mono">
                        {formatCurrency(transaction.valorPositivo)}
                      </TableCell>
                      <TableCell>{transaction.grupo}</TableCell>
                      <TableCell>{transaction.subgrupo}</TableCell>
                      <TableCell>
                        <Badge variant="outline">
                          {transaction.origem_classificacao}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {transaction.duplicateInfo?.similarity ? (
                          <span className="text-sm text-gray-600">
                            {Math.round(transaction.duplicateInfo.similarity * 100)}%
                          </span>
                        ) : '-'}
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
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Editar Classificação</DialogTitle>
              <DialogDescription>
                Ajuste a classificação manualmente
              </DialogDescription>
            </DialogHeader>
            
            {editingTransaction && (
              <div className="space-y-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-blue-900 font-medium">Dados da Transação:</p>
                  <p className="text-sm text-blue-700">
                    {editingTransaction.data} • {formatCurrency(editingTransaction.valorPositivo)}
                  </p>
                  <p className="text-sm text-blue-700">
                    {editingTransaction.tipoTransacao}
                  </p>
                  {editingTransaction.duplicateInfo?.isDuplicate && (
                    <p className="text-sm text-yellow-700 mt-2">
                      ⚠️ Esta transação foi identificada como duplicata (similaridade: {Math.round((editingTransaction.duplicateInfo.similarity || 0) * 100)}%)
                    </p>
                  )}
                </div>

                <div>
                  <Label htmlFor="estabelecimento">Estabelecimento</Label>
                  <Input
                    id="estabelecimento"
                    value={editForm.estabelecimento}
                    onChange={(e) => setEditForm(prev => ({ ...prev, estabelecimento: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="tipoGasto">Tipo de Gasto</Label>
                  <Input
                    id="tipoGasto"
                    value={editForm.tipoGasto}
                    onChange={(e) => setEditForm(prev => ({ ...prev, tipoGasto: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="grupo">Grupo</Label>
                  <Input
                    id="grupo"
                    value={editForm.grupo}
                    onChange={(e) => setEditForm(prev => ({ ...prev, grupo: e.target.value }))}
                  />
                </div>

                <div>
                  <Label htmlFor="subgrupo">Subgrupo</Label>
                  <Input
                    id="subgrupo"
                    value={editForm.subgrupo}
                    onChange={(e) => setEditForm(prev => ({ ...prev, subgrupo: e.target.value }))}
                  />
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

        {/* Dialog de confirmação de importação */}
        <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Confirmar importação</DialogTitle>
              <DialogDescription>
                Você está prestes a importar{' '}
                <strong>{transactions.filter(t => t.selected).length} transações</strong>.
                Deseja continuar?
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
                Cancelar
              </Button>
              <Button onClick={handleDoConfirm} disabled={isConfirming}>
                {isConfirming ? 'Importando...' : 'Confirmar importação'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}

// Hook para usar em outras páginas que precisam do processamento
export function useFileUpload() {
  const [processing, setProcessing] = React.useState(false)
  const [error, setError] = React.useState('')

  const uploadAndProcess = async (file: File): Promise<{ transactions: Transaction[], summary: ClassificationSummary }> => {
    setProcessing(true)
    setError('')

    try {
      // Processar arquivo
      const formData = new FormData()
      formData.append('file', file)

      const processResponse = await fetch('/api/upload/process', {
        method: 'POST',
        body: formData,
      })

      if (!processResponse.ok) {
        const errorData = await processResponse.json()
        throw new Error(errorData.error || 'Erro no processamento')
      }

      const processData = await processResponse.json()
      
      // Classificar com IA
      const classifyResponse = await fetch('/api/upload/classify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transactions: processData.transactions,
          sessionId: Date.now().toString()
        }),
      })

      if (!classifyResponse.ok) {
        const errorData = await classifyResponse.json()
        throw new Error(errorData.error || 'Erro na classificação')
      }

      const classifyData = await classifyResponse.json()
      
      return {
        transactions: processData.transactions.map((transaction: any, index: number) => ({
          ...transaction,
          ...classifyData.transactions[index],
          duplicateInfo: classifyData.duplicates[index]
        })),
        summary: classifyData.summary
      }
      
    } catch (error) {
      setError((error as Error).message)
      throw error
    } finally {
      setProcessing(false)
    }
  }

  return {
    uploadAndProcess,
    processing,
    error
  }
}