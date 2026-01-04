"use client"

import * as React from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Check, X, FileText, Filter, Info } from "lucide-react"
import { format as formatDate } from "date-fns"
import { ptBR } from "date-fns/locale"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import DashboardLayout from "@/components/dashboard-layout"

interface TransacaoClassificada {
  // Campos originais
  Data: string
  Estabelecimento: string
  Valor: number
  ValorPositivo: number
  TipoTransacao: string
  
  // Identificadores
  IdTransacao: string
  IdParcela: string | null
  
  // Informações de parcela
  EstabelecimentoBase: string
  ParcelaAtual: number | null
  TotalParcelas: number | null
  TemParcela: boolean
  
  // Classificação
  GRUPO: string
  SUBGRUPO: string
  TipoGasto: string
  CategoriaGeral: string
  origem_classificacao: string
  IgnorarDashboard: boolean
  ValidarIA: string
  MarcacaoIA: string
  
  // Metadados
  origem: string
  data_processamento: string
}

interface Metadata {
  banco: string
  cartao: string
  nomeArquivo: string
  mesFatura: string
  totalRegistros: number
  somaTotal: number
  estatisticas?: {
    total: number
    nivel_0_id_parcela: number
    nivel_1_fatura_cartao: number
    nivel_2_ignorar: number
    nivel_3_base_padroes: number
    nivel_4_journal_entries: number
    nivel_5_palavras_chave: number
    nivel_6_nao_encontrado: number
  }
}

interface PreviewResponse {
  metadata: Metadata
  transacoes: TransacaoClassificada[]
}

interface ErrorResponse {
  error: string
  errorCode?: string
  details?: any
  suggestedAction?: string
}

// Mapeamento de cores para cada nível de classificação
const nivelColors: Record<string, { bg: string; text: string; label: string }> = {
  'IdParcela': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Parcela' },
  'Fatura Cartão': { bg: 'bg-purple-100', text: 'text-purple-800', label: 'Fatura' },
  'Ignorar - Nome do Titular': { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Titular' },
  'Ignorar - Lista Admin': { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Ignorar' },
  'Base_Padroes': { bg: 'bg-green-100', text: 'text-green-800', label: 'Padrão' },
  'Journal Entries': { bg: 'bg-cyan-100', text: 'text-cyan-800', label: 'Histórico' },
  'Palavras-chave': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Keyword' },
  'Não Encontrado': { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Manual' },
}

export default function UploadPreviewEnhancedPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string

  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [metadata, setMetadata] = React.useState<Metadata | null>(null)
  const [transacoes, setTransacoes] = React.useState<TransacaoClassificada[]>([])
  const [isConfirming, setIsConfirming] = React.useState(false)

  // Filtros
  const [filtroOrigem, setFiltroOrigem] = React.useState<string>('todos')
  const [filtroEstabelecimento, setFiltroEstabelecimento] = React.useState<string>('')
  const [filtroGrupo, setFiltroGrupo] = React.useState<string>('todos')
  const [mostrarIgnoradas, setMostrarIgnoradas] = React.useState<boolean>(true)

  React.useEffect(() => {
    fetchPreviewData()
  }, [sessionId])

  const fetchPreviewData = async () => {
    try {
      setLoading(true)
      setError(null)
      
      console.log('🔍 Buscando preview para sessionId:', sessionId)
      const response = await fetch(`/api/upload/process-classify/${sessionId}`)
      
      console.log('📡 Response status:', response.status)
      
      if (!response.ok) {
        let errorData: ErrorResponse
        try {
          errorData = await response.json()
        } catch {
          errorData = { error: `Erro HTTP ${response.status}: ${response.statusText}` }
        }
        
        console.error('❌ Erro na resposta:', errorData)
        
        // Formatar mensagem de erro amigável
        const errorMsg = errorData.errorCode 
          ? `[${errorData.errorCode}] ${errorData.error}`
          : errorData.error || 'Erro ao carregar preview'
        
        if (errorData.details) {
          console.error('📋 Detalhes do erro:', errorData.details)
        }
        
        throw new Error(errorMsg)
      }

      const data: PreviewResponse = await response.json()
      console.log('✅ Preview carregado:', data.metadata.totalRegistros, 'transações')
      setMetadata(data.metadata)
      setTransacoes(data.transacoes)
    } catch (err) {
      let errorMsg = 'Erro desconhecido ao processar preview'
      
      if (err instanceof Error) {
        errorMsg = err.message
      } else if (typeof err === 'object' && err !== null) {
        errorMsg = JSON.stringify(err)
      }
      
      console.error('💥 Erro ao buscar preview:', err)
      setError(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    try {
      await fetch(`/api/upload/preview/${sessionId}`, {
        method: 'DELETE'
      })
      
      router.push('/upload')
    } catch (err) {
      console.error('Erro ao cancelar:', err)
      router.push('/upload')
    }
  }

  const handleConfirm = async () => {
    setIsConfirming(true)
    try {
      const response = await fetch(`/api/upload/confirm/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transacoes })
      })

      if (!response.ok) {
        throw new Error('Falha ao confirmar importação')
      }

      router.push('/transactions?imported=true')
    } catch (err) {
      console.error('Erro ao confirmar:', err)
      setError('Falha ao confirmar importação')
    } finally {
      setIsConfirming(false)
    }
  }

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatMesFatura = (mesFatura: string) => {
    const [ano, mes] = mesFatura.split('-')
    const data = new Date(parseInt(ano), parseInt(mes) - 1)
    return formatDate(data, "MMMM 'de' yyyy", { locale: ptBR })
  }

  // Filtrar transações
  const transacoesFiltradas = React.useMemo(() => {
    return transacoes.filter(t => {
      // Filtro de origem
      if (filtroOrigem !== 'todos' && t.origem_classificacao !== filtroOrigem) {
        return false
      }

      // Filtro de estabelecimento
      if (filtroEstabelecimento && !t.Estabelecimento.toLowerCase().includes(filtroEstabelecimento.toLowerCase())) {
        return false
      }

      // Filtro de grupo
      if (filtroGrupo !== 'todos' && t.GRUPO !== filtroGrupo) {
        return false
      }

      // Mostrar/ocultar ignoradas
      if (!mostrarIgnoradas && t.IgnorarDashboard) {
        return false
      }

      return true
    })
  }, [transacoes, filtroOrigem, filtroEstabelecimento, filtroGrupo, mostrarIgnoradas])

  // Obter listas únicas para filtros
  const origensUnicas = React.useMemo(() => {
    return Array.from(new Set(transacoes.map(t => t.origem_classificacao)))
  }, [transacoes])

  const gruposUnicos = React.useMemo(() => {
    return Array.from(new Set(transacoes.map(t => t.GRUPO).filter(g => g !== '')))
  }, [transacoes])

  const getBadgeInfo = (origem: string) => {
    return nivelColors[origem] || nivelColors['Não Encontrado']
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-[70vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Processando e classificando...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !metadata) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-[70vh]">
          <Card className="max-w-md">
            <CardHeader>
              <CardTitle className="text-destructive flex items-center gap-2">
                <X className="h-5 w-5" />
                Erro ao Carregar Preview
              </CardTitle>
              <CardDescription className="text-base space-y-2">
                <p className="font-medium">{error || 'Dados não encontrados'}</p>
                <p className="text-sm text-muted-foreground">
                  Verifique se o arquivo foi processado corretamente ou tente fazer o upload novamente.
                </p>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => router.push('/upload')} variant="outline" className="w-full">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Voltar para Upload
              </Button>
            </CardContent>
          </Card>
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
            <h1 className="text-3xl font-bold tracking-tight">Preview com Classificação IA</h1>
            <p className="text-muted-foreground mt-2">
              Transações processadas e classificadas automaticamente
            </p>
          </div>
          <Button onClick={handleCancel} variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Cancelar
          </Button>
        </div>

        {/* Metadata Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Informações do Arquivo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Banco</p>
                <p className="font-semibold">{metadata.banco}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Cartão</p>
                <p className="font-semibold">{metadata.cartao}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Arquivo</p>
                <p className="font-semibold text-sm">{metadata.nomeArquivo}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Mês Fatura</p>
                <p className="font-semibold">{formatMesFatura(metadata.mesFatura)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total de Lançamentos</p>
                <p className="font-semibold">{metadata.totalRegistros}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Soma Total</p>
                <p className="font-semibold text-lg">{formatCurrency(metadata.somaTotal)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Estatísticas de Classificação */}
        {metadata.estatisticas && (
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Estatísticas de Classificação</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('IdParcela').bg} ${getBadgeInfo('IdParcela').text}`}>
                    {metadata.estatisticas.nivel_0_id_parcela}
                  </Badge>
                  <span>Parcelas</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('Fatura Cartão').bg} ${getBadgeInfo('Fatura Cartão').text}`}>
                    {metadata.estatisticas.nivel_1_fatura_cartao}
                  </Badge>
                  <span>Faturas</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('Ignorar - Lista Admin').bg} ${getBadgeInfo('Ignorar - Lista Admin').text}`}>
                    {metadata.estatisticas.nivel_2_ignorar}
                  </Badge>
                  <span>Ignoradas</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('Base_Padroes').bg} ${getBadgeInfo('Base_Padroes').text}`}>
                    {metadata.estatisticas.nivel_3_base_padroes}
                  </Badge>
                  <span>Padrões</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('Journal Entries').bg} ${getBadgeInfo('Journal Entries').text}`}>
                    {metadata.estatisticas.nivel_4_journal_entries}
                  </Badge>
                  <span>Histórico</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('Palavras-chave').bg} ${getBadgeInfo('Palavras-chave').text}`}>
                    {metadata.estatisticas.nivel_5_palavras_chave}
                  </Badge>
                  <span>Keywords</span>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className={`${getBadgeInfo('Não Encontrado').bg} ${getBadgeInfo('Não Encontrado').text}`}>
                    {metadata.estatisticas.nivel_6_nao_encontrado}
                  </Badge>
                  <span>Manuais</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Filter className="h-4 w-4" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="filtro-origem">Origem Classificação</Label>
                <Select value={filtroOrigem} onValueChange={setFiltroOrigem}>
                  <SelectTrigger id="filtro-origem">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todas</SelectItem>
                    {origensUnicas.map(origem => (
                      <SelectItem key={origem} value={origem}>{origem}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="filtro-grupo">Grupo</Label>
                <Select value={filtroGrupo} onValueChange={setFiltroGrupo}>
                  <SelectTrigger id="filtro-grupo">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="todos">Todos</SelectItem>
                    {gruposUnicos.map(grupo => (
                      <SelectItem key={grupo} value={grupo}>{grupo}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="filtro-estabelecimento">Estabelecimento</Label>
                <Input
                  id="filtro-estabelecimento"
                  placeholder="Buscar..."
                  value={filtroEstabelecimento}
                  onChange={(e) => setFiltroEstabelecimento(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="filtro-ignoradas">Exibir</Label>
                <Select 
                  value={mostrarIgnoradas ? 'sim' : 'nao'} 
                  onValueChange={(v) => setMostrarIgnoradas(v === 'sim')}
                >
                  <SelectTrigger id="filtro-ignoradas">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sim">Com Ignoradas</SelectItem>
                    <SelectItem value="nao">Sem Ignoradas</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="mt-4 text-sm text-muted-foreground flex items-center gap-2">
              <Info className="h-4 w-4" />
              <span>
                Mostrando {transacoesFiltradas.length} de {transacoes.length} transações
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <CardHeader>
            <CardTitle>Transações Classificadas</CardTitle>
            <CardDescription>
              {transacoesFiltradas.length} transações com classificação automática
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">Data</TableHead>
                    <TableHead>Estabelecimento</TableHead>
                    <TableHead>Classificação</TableHead>
                    <TableHead>Origem</TableHead>
                    <TableHead className="text-right w-[120px]">Valor</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transacoesFiltradas.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center text-muted-foreground">
                        Nenhuma transação encontrada com os filtros aplicados
                      </TableCell>
                    </TableRow>
                  ) : (
                    transacoesFiltradas.map((transacao, idx) => {
                      const badgeInfo = getBadgeInfo(transacao.origem_classificacao)
                      
                      return (
                        <TableRow key={idx} className={transacao.IgnorarDashboard ? 'bg-yellow-50' : ''}>
                          <TableCell className="font-mono text-sm">
                            {transacao.Data}
                          </TableCell>
                          <TableCell>
                            <div className="flex flex-col">
                              <span className="font-medium">{transacao.Estabelecimento}</span>
                              {transacao.TemParcela && (
                                <span className="text-xs text-muted-foreground">
                                  Parcela {transacao.ParcelaAtual}/{transacao.TotalParcelas}
                                </span>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            {transacao.GRUPO ? (
                              <div className="flex flex-col text-sm">
                                <span className="font-medium">{transacao.GRUPO}</span>
                                {transacao.SUBGRUPO && (
                                  <span className="text-xs text-muted-foreground">
                                    {transacao.SUBGRUPO}
                                  </span>
                                )}
                              </div>
                            ) : (
                              <span className="text-sm text-muted-foreground italic">Não classificado</span>
                            )}
                          </TableCell>
                          <TableCell>
                            <Badge className={`${badgeInfo.bg} ${badgeInfo.text} text-xs`}>
                              {badgeInfo.label}
                            </Badge>
                            {transacao.IgnorarDashboard && (
                              <Badge variant="outline" className="ml-1 text-xs">Ignorar</Badge>
                            )}
                          </TableCell>
                          <TableCell className="text-right">
                            <span className={transacao.Valor < 0 ? "text-red-600 font-medium" : "text-green-600 font-medium"}>
                              {formatCurrency(transacao.Valor)}
                            </span>
                          </TableCell>
                        </TableRow>
                      )
                    })
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Button onClick={handleCancel} variant="outline" size="lg">
            <X className="mr-2 h-4 w-4" />
            Cancelar Importação
          </Button>
          <Button 
            onClick={handleConfirm} 
            size="lg"
            disabled={isConfirming || transacoes.length === 0}
          >
            {isConfirming ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Salvando...
              </>
            ) : (
              <>
                <Check className="mr-2 h-4 w-4" />
                Confirmar e Salvar ({transacoes.length})
              </>
            )}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  )
}
