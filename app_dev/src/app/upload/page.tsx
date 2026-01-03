"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { UploadDialog } from "@/components/upload-dialog"
import { Upload, FileText, PlusCircle, CheckCircle, XCircle, Clock, FileX } from "lucide-react"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import DashboardLayout from "@/components/dashboard-layout"

interface UploadHistory {
  id: number
  fileName: string
  bank: string
  creditCard?: string
  uploadDate: string
  fileSize: number
  status: 'processed' | 'processing' | 'error'
  transactionsCount: number
  type: 'fatura' | 'extrato'
  error?: string
}

export default function UploadPage() {
  const [uploadDialogOpen, setUploadDialogOpen] = React.useState(false)
  const [uploadHistory, setUploadHistory] = React.useState<UploadHistory[]>([])
  const [loading, setLoading] = React.useState(true)

  const fetchUploadHistory = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/upload/history')
      if (response.ok) {
        const data = await response.json()
        setUploadHistory(data)
      }
    } catch (error) {
      console.error('Erro ao buscar histórico:', error)
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    fetchUploadHistory()
  }, [])

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'processed':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      default:
        return <FileX className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'processed':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Processado</Badge>
      case 'processing':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Processando</Badge>
      case 'error':
        return <Badge variant="destructive">Erro</Badge>
      default:
        return <Badge variant="outline">Desconhecido</Badge>
    }
  }

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Upload de Arquivos</h1>
          <p className="text-muted-foreground">
            Importe faturas de cartão de crédito e extratos bancários
          </p>
        </div>
        <Button onClick={() => setUploadDialogOpen(true)}>
          <PlusCircle className="mr-2 h-4 w-4" />
          Novo Upload
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card 
          className="cursor-pointer hover:bg-muted/50 transition-colors"
          onClick={() => setUploadDialogOpen(true)}
        >
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <Upload className="h-5 w-5 text-primary" />
              Upload Rápido
            </CardTitle>
            <CardDescription>
              Importe seus arquivos financeiros de forma rápida e fácil
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Clique aqui para começar o upload de faturas de cartão ou extratos bancários
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Formatos Aceitos
            </CardTitle>
            <CardDescription>
              Tipos de arquivo suportados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">PDF (com ou sem senha)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">Excel (XLS/XLSX)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">OFX</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm">CSV</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-primary" />
              Bancos Suportados
            </CardTitle>
            <CardDescription>
              Instituições financeiras
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm">Banco Itaú</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm">Bradesco</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm">Santander</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm">BTG Pactual</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Área de histórico de uploads */}
      <Card>
        <CardHeader>
          <CardTitle>Histórico de Uploads</CardTitle>
          <CardDescription>
            Acompanhe seus uploads recentes e seu status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-muted-foreground">Carregando histórico...</p>
            </div>
          ) : uploadHistory.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="mx-auto h-12 w-12 opacity-50 mb-4" />
              <p>Nenhum upload realizado ainda</p>
              <p className="text-sm">Seus uploads aparecerão aqui após a importação</p>
            </div>
          ) : (
            <div className="space-y-4">
              {uploadHistory.map((upload) => (
                <div
                  key={upload.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(upload.status)}
                    <div>
                      <p className="font-medium">{upload.fileName}</p>
                      <p className="text-sm text-muted-foreground">
                        {upload.bank} {upload.creditCard ? `• ${upload.creditCard}` : ''} • {upload.type === 'fatura' ? 'Fatura' : 'Extrato'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(upload.uploadDate)} • {formatFileSize(upload.fileSize)}
                      </p>
                      {upload.error && (
                        <p className="text-xs text-red-600 mt-1">{upload.error}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {upload.status === 'processed' && (
                      <span className="text-sm text-muted-foreground">
                        {upload.transactionsCount} transações
                      </span>
                    )}
                    {getStatusBadge(upload.status)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <UploadDialog 
        open={uploadDialogOpen} 
        onOpenChange={setUploadDialogOpen}
        onUploadSuccess={fetchUploadHistory}
      />
      </div>
    </DashboardLayout>
  )
}