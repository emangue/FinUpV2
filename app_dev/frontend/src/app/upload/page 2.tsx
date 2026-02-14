"use client"

import * as React from "react"
import { Button } from "@/components/ui/button"
import { UploadDialog } from "@/features/upload"
import { Upload, FileText, PlusCircle, CheckCircle, XCircle, Clock, FileX } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
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
  session_id: string
  banco: string
  tipo_documento: string
  nome_arquivo: string
  nome_cartao?: string
  final_cartao?: string
  mes_fatura?: string
  status: 'processing' | 'success' | 'error' | 'cancelled'
  total_registros: number
  transacoes_importadas: number
  transacoes_duplicadas: number
  classification_stats?: {
    base_parcelas: number
    base_padroes: number
    journal_entries: number
    marcas_gerais: number
    nao_classificado: number
  }
  data_upload: string
  data_confirmacao?: string
  error_message?: string
}

export default function UploadPage() {
  const [uploadDialogOpen, setUploadDialogOpen] = React.useState(false)
  const [compatibilityDialogOpen, setCompatibilityDialogOpen] = React.useState(false)
  const [uploadHistory, setUploadHistory] = React.useState<UploadHistory[]>([])
  const [loading, setLoading] = React.useState(true)

  const fetchUploadHistory = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/upload/history')
      if (response.ok) {
        const data = await response.json()
        setUploadHistory(data.uploads || [])
      }
    } catch (error) {
      console.error('Erro ao buscar histórico:', error)
      setUploadHistory([])
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
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case 'processing':
        return <Clock className="h-4 w-4 text-yellow-600" />
      case 'error':
        return <XCircle className="h-4 w-4 text-red-600" />
      case 'cancelled':
        return <FileX className="h-4 w-4 text-gray-600" />
      default:
        return <FileX className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Sucesso</Badge>
      case 'processing':
        return <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">Processando</Badge>
      case 'error':
        return <Badge variant="destructive">Erro</Badge>
      case 'cancelled':
        return <Badge variant="secondary" className="bg-gray-100 text-gray-800">Cancelado</Badge>
      default:
        return <Badge variant="secondary">Desconhecido</Badge>
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
                <span className="text-sm">CSV</span>
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
                <span className="text-sm">PDF</span>
              </div>
            </div>
            <Button
              variant="link"
              className="mt-4 p-0 h-auto text-blue-600"
              onClick={() => setCompatibilityDialogOpen(true)}
            >
              Ver compatibilidade por banco →
            </Button>
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
                <span className="text-sm">BTG Pactual</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm">Banco do Brasil</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-sm">Mercado Pago</span>
              </div>
            </div>
            <Button
              variant="link"
              className="mt-4 p-0 h-auto text-blue-600"
              onClick={() => setCompatibilityDialogOpen(true)}
            >
              Ver compatibilidade por formato →
            </Button>
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
                      <p className="font-medium">{upload.nome_arquivo}</p>
                      <p className="text-sm text-muted-foreground">
                        {upload.banco} {upload.nome_cartao ? `• ${upload.nome_cartao}` : ''} • {upload.tipo_documento === 'fatura' ? 'Fatura' : 'Extrato'}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {formatDate(upload.data_upload)}
                      </p>
                      {upload.error_message && (
                        <p className="text-xs text-red-600 mt-1">{upload.error_message}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {upload.status === 'success' && (
                      <div className="text-sm text-muted-foreground text-right">
                        <p className="font-medium text-green-600">{upload.transacoes_importadas} importadas</p>
                        {upload.transacoes_duplicadas > 0 && (
                          <p className="text-xs text-amber-600">{upload.transacoes_duplicadas} duplicadas</p>
                        )}
                      </div>
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

      <Dialog open={compatibilityDialogOpen} onOpenChange={setCompatibilityDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Compatibilidade de Formatos por Banco</DialogTitle>
            <DialogDescription>
              Status de suporte para cada combinação de banco e formato de arquivo
            </DialogDescription>
          </DialogHeader>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3 font-medium text-sm">Banco</th>
                  <th className="text-center p-3 font-medium text-sm">CSV</th>
                  <th className="text-center p-3 font-medium text-sm">Excel</th>
                  <th className="text-center p-3 font-medium text-sm">PDF</th>
                  <th className="text-center p-3 font-medium text-sm">OFX</th>
                </tr>
              </thead>
              <tbody>
                {/* Itaú */}
                <tr className="border-b hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">Banco Itaú</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                </tr>
                {/* BTG */}
                <tr className="border-b hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">BTG Pactual</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                </tr>
                {/* Banco do Brasil */}
                <tr className="border-b hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">Banco do Brasil</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                </tr>
                {/* Mercado Pago */}
                <tr className="border-b hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">Mercado Pago</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-green-500 hover:bg-green-600 text-white">OK</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                </tr>
                {/* Santander */}
                <tr className="border-b hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">Santander</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                </tr>
                {/* Bradesco */}
                <tr className="border-b hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">Bradesco</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                </tr>
                {/* Outros */}
                <tr className="hover:bg-muted/50">
                  <td className="p-3 font-medium text-sm">Outros</td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                  <td className="p-3 text-center">
                    <Badge className="bg-red-500 hover:bg-red-600 text-white">TBD</Badge>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex items-center gap-6 text-xs text-muted-foreground">
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500 text-white h-5">OK</Badge>
              <span>Suportado</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-yellow-500 text-white h-5">WIP</Badge>
              <span>Em desenvolvimento</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge className="bg-red-500 text-white h-5">TBD</Badge>
              <span>A ser desenvolvido</span>
            </div>
          </div>
        </DialogContent>
      </Dialog>
      </div>
    </DashboardLayout>
  )
}