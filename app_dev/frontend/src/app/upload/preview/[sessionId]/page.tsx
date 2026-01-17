"use client"

import * as React from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Check, X, FileText } from "lucide-react"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import DashboardLayout from "@/components/dashboard-layout"

interface PreviewData {
  id: number
  banco: string
  cartao: string
  nome_arquivo: string
  mes_fatura: string
  data: string
  lancamento: string
  valor: number
  created_at: string
  id_transacao?: string
  id_parcela?: string
  estabelecimento_base?: string
  parcela_atual?: number
  total_parcelas?: number
  valor_positivo?: number
  grupo?: string
  subgrupo?: string
  tipo_gasto?: string
  categoria_geral?: string
  origem_classificacao?: string
  marcacao_ia?: string
  is_duplicate?: boolean
  duplicate_reason?: string
}

interface Metadata {
  banco: string
  cartao: string
  nomeArquivo: string
  mesFatura: string
  totalRegistros: number
  somaTotal: number
  tipoDocumento?: string
  balanceValidation?: {
    saldo_inicial: number
    saldo_final: number
    soma_transacoes: number
    is_valid: boolean
    diferenca: number
  }
}

interface GruposSubgrupos {
  grupos: string[]
  subgruposPorGrupo: Record<string, string[]>
}

export default function UploadPreviewPage() {
  const params = useParams()
  const router = useRouter()
  const sessionId = params.sessionId as string

  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [metadata, setMetadata] = React.useState<Metadata | null>(null)
  const [registros, setRegistros] = React.useState<PreviewData[]>([])
  const [isConfirming, setIsConfirming] = React.useState(false)
  const [gruposSubgrupos, setGruposSubgrupos] = React.useState<GruposSubgrupos>({ grupos: [], subgruposPorGrupo: {} })
  const [activeFilter, setActiveFilter] = React.useState<string>('todas')

  React.useEffect(() => {
    fetchPreviewData()
    fetchGruposSubgrupos()
  }, [sessionId])

  // Auto-filtrar para "Não Classificadas" se houver
  React.useEffect(() => {
    if (registros.length > 0) {
      const naoClassificadas = registros.filter(r => !r.grupo || !r.subgrupo || r.origem_classificacao === 'Não Classificado')
      if (naoClassificadas.length > 0) {
        setActiveFilter('nao_classificadas')
      }
    }
  }, [registros])

  const fetchPreviewData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`/api/upload/preview/${sessionId}`)
      
      if (!response.ok) {
        throw new Error('Falha ao carregar dados do preview')
      }

      const data = await response.json()
      
      // Backend retorna: { success, sessionId, totalRegistros, dados, banco, tipo_documento, nome_arquivo, nome_cartao, mes_fatura, balance_validation }
      if (data.dados && data.dados.length > 0) {
        const firstRecord = data.dados[0]
        
        // Construir metadata a partir dos dados do backend (priority) ou firstRecord (fallback)
        const metadata: Metadata = {
          banco: data.banco || firstRecord.banco || '',
          cartao: firstRecord.cartao || '',
          nomeArquivo: data.nome_arquivo || firstRecord.nome_arquivo || '',
          mesFatura: data.mes_fatura || firstRecord.mes_fatura || '',
          totalRegistros: data.totalRegistros,
          somaTotal: data.dados.reduce((sum: number, r: any) => sum + (r.valor || 0), 0),
          tipoDocumento: data.tipo_documento || '',
          balanceValidation: data.balance_validation || undefined
        }
        
        setMetadata(metadata)
        setRegistros(data.dados)
      } else {
        throw new Error('Nenhum dado encontrado para esta sessão')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  const fetchGruposSubgrupos = async () => {
    try {
      const response = await fetch('/api/categories/grupos-subgrupos')
      if (response.ok) {
        const data = await response.json()
        setGruposSubgrupos(data)
      }
    } catch (err) {
      console.error('Erro ao buscar grupos/subgrupos:', err)
    }
  }

  const handleGrupoChange = async (previewId: number, grupo: string) => {
    try {
      const response = await fetch(`/api/upload/preview/${sessionId}/${previewId}?grupo=${grupo}`, {
        method: 'PATCH'
      })
      
      if (response.ok) {
        // Atualizar local
        setRegistros(prev => prev.map(r => 
          r.id === previewId ? { ...r, grupo, subgrupo: undefined } : r
        ))
      }
    } catch (err) {
      console.error('Erro ao atualizar grupo:', err)
    }
  }

  const handleSubgrupoChange = async (previewId: number, subgrupo: string) => {
    try {
      const response = await fetch(`/api/upload/preview/${sessionId}/${previewId}?subgrupo=${subgrupo}`, {
        method: 'PATCH'
      })
      
      if (response.ok) {
        // Atualizar local
        setRegistros(prev => prev.map(r => 
          r.id === previewId ? { ...r, subgrupo } : r
        ))
      }
    } catch (err) {
      console.error('Erro ao atualizar subgrupo:', err)
    }
  }

  const handleCancel = async () => {
    try {
      // Deletar preview
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
      console.log('Confirmando importação de', registros.length, 'registros')
      
      // Chamar endpoint de confirmação correto (session_id na URL)
      const response = await fetch(`/api/upload/confirm/${sessionId}`, {
        method: 'POST'
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Erro ao confirmar importação')
      }
      
      const result = await response.json()
      console.log('✅ Importação confirmada:', result)
      
      // Redirecionar para transações
      router.push('/transactions')
    } catch (err) {
      console.error('❌ Erro ao confirmar:', err)
      setError(err instanceof Error ? err.message : 'Falha ao confirmar importação')
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
    // mesFatura pode vir como "202511" ou "2025-11"
    let ano: string, mes: string
    
    if (mesFatura.includes('-')) {
      [ano, mes] = mesFatura.split('-')
    } else if (mesFatura.length === 6) {
      // Formato YYYYMM
      ano = mesFatura.substring(0, 4)
      mes = mesFatura.substring(4, 6)
    } else {
      return mesFatura // Retornar original se não reconhecer formato
    }
    
    const data = new Date(parseInt(ano), parseInt(mes) - 1)
    return formatDate(data, "MMMM 'de' yyyy", { locale: ptBR })
  }

  // Contar não classificadas e duplicadas
  const contadores = React.useMemo(() => {
    const duplicadas = registros.filter(r => r.is_duplicate)
    const naoDuplicadas = registros.filter(r => !r.is_duplicate)
    
    const naoClassificadas = naoDuplicadas.filter(r => !r.grupo || !r.subgrupo || r.origem_classificacao === 'Não Classificado')
    const validas = naoDuplicadas.filter(r => r.grupo && r.subgrupo)
    const classificadas = naoDuplicadas.filter(r => r.grupo && r.subgrupo)
    const baseParcelas = naoDuplicadas.filter(r => r.origem_classificacao === 'Base Parcelas')
    const basePadroes = naoDuplicadas.filter(r => r.origem_classificacao === 'Base Padrões')
    const journalEntries = naoDuplicadas.filter(r => r.origem_classificacao === 'Journal Entries')
    const regrasGenericas = naoDuplicadas.filter(r => r.origem_classificacao === 'Regras Genéricas')
    
    return {
      todas: registros.length,
      naoDuplicadas: naoDuplicadas.length,
      naoClassificadas: naoClassificadas.length,
      duplicadas: duplicadas.length,
      validas: validas.length,
      classificadas: classificadas.length,
      baseParcelas: baseParcelas.length,
      basePadroes: basePadroes.length,
      journalEntries: journalEntries.length,
      regrasGenericas: regrasGenericas.length
    }
  }, [registros])

  // Filtrar registros baseado na aba ativa (ordem do processo cascata: Nível 1-2-3-4)
  // Duplicadas são excluídas de todos os filtros exceto 'todas' e 'duplicadas'
  const filteredRegistros = React.useMemo(() => {
    switch (activeFilter) {
      case 'classificadas':
        return registros.filter(r => !r.is_duplicate && r.grupo && r.subgrupo)
      case 'base_parcelas':
        return registros.filter(r => !r.is_duplicate && r.origem_classificacao === 'Base Parcelas')
      case 'base_padroes':
        return registros.filter(r => !r.is_duplicate && r.origem_classificacao === 'Base Padrões')
      case 'journal_entries':
        return registros.filter(r => !r.is_duplicate && r.origem_classificacao === 'Journal Entries')
      case 'regras_genericas':
        return registros.filter(r => !r.is_duplicate && r.origem_classificacao === 'Regras Genéricas')
      case 'nao_classificadas':
        return registros.filter(r => !r.is_duplicate && (!r.grupo || !r.subgrupo || r.origem_classificacao === 'Não Classificado'))
      case 'duplicadas':
        return registros.filter(r => r.is_duplicate)
      default:
        return registros
    }
  }, [registros, activeFilter])

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-[70vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Carregando preview...</p>
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
              <CardTitle className="text-destructive">Erro</CardTitle>
              <CardDescription>{error || 'Dados não encontrados'}</CardDescription>
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
            <h1 className="text-3xl font-bold tracking-tight">Preview de Importação</h1>
            <p className="text-muted-foreground mt-2">
              Revise os dados antes de confirmar a importação
            </p>
          </div>
          <Button onClick={handleCancel} variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Cancelar
          </Button>
        </div>

        {/* Status de Classificação */}
        {contadores.naoClassificadas > 0 ? (
          <Card className="border-amber-200 bg-amber-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <X className="h-5 w-5 text-amber-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-amber-900">
                    {contadores.naoClassificadas} {contadores.naoClassificadas === 1 ? 'transação' : 'transações'} sem classificação
                  </h3>
                  <p className="text-sm text-amber-700 mt-1">
                    Complete a classificação antes de confirmar a importação. 
                    {contadores.validas > 0 && ` ${contadores.validas} de ${contadores.todas - contadores.duplicadas} transações já classificadas.`}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-green-200 bg-green-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <Check className="h-5 w-5 text-green-600 mt-0.5" />
                <div className="flex-1">
                  <h3 className="font-semibold text-green-900">
                    Arquivo pronto para importação
                  </h3>
                  <p className="text-sm text-green-700 mt-1">
                    {contadores.validas} {contadores.validas === 1 ? 'transação classificada' : 'transações classificadas'}
                    {contadores.duplicadas > 0 && ` • ${contadores.duplicadas} duplicadas serão ignoradas`}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

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
              
              {/* Mostrar Mês Fatura ou Validação de Saldo baseado no tipo_documento */}
              {metadata.tipoDocumento === 'extrato' && metadata.balanceValidation ? (
                <>
                  <div>
                    <p className="text-sm text-muted-foreground">Saldo Inicial</p>
                    <p className="font-semibold">{formatCurrency(metadata.balanceValidation.saldo_inicial)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Saldo Final</p>
                    <p className="font-semibold">{formatCurrency(metadata.balanceValidation.saldo_final)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Validação de Saldo</p>
                    <div className="flex items-center gap-2">
                      {metadata.balanceValidation.is_valid ? (
                        <>
                          <Check className="h-5 w-5 text-green-600" />
                          <span className="font-semibold text-green-600">Válido</span>
                        </>
                      ) : (
                        <>
                          <X className="h-5 w-5 text-amber-600" />
                          <span className="font-semibold text-amber-600">
                            Diferença: {formatCurrency(metadata.balanceValidation.diferenca)}
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <div>
                  <p className="text-sm text-muted-foreground">Mês Fatura</p>
                  <p className="font-semibold">{formatMesFatura(metadata.mesFatura)}</p>
                </div>
              )}
              
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

        {/* Botão de Confirmação Superior - Mostrar apenas quando estiver tudo OK */}
        {contadores.naoClassificadas === 0 && registros.length > 0 && (
          <div className="flex justify-end gap-4">
            <Button onClick={handleCancel} variant="outline" size="lg">
              <X className="mr-2 h-4 w-4" />
              Cancelar Importação
            </Button>
            <Button 
              onClick={handleConfirm} 
              size="lg"
              disabled={isConfirming}
            >
              {isConfirming ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processando...
                </>
              ) : (
                <>
                  <Check className="mr-2 h-4 w-4" />
                  Confirmar Importação ({contadores.validas} transações)
                </>
              )}
            </Button>
          </div>
        )}

        {/* Table */}
        <Card>
          <CardHeader>
            <CardTitle>Lançamentos Detectados</CardTitle>
            <CardDescription>
              {activeFilter === 'todas' 
                ? `${registros.length} lançamentos prontos para importação`
                : `${filteredRegistros.length} de ${registros.length} lançamentos`
              }
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Filtros de Origem - Abas */}
            <div className="mb-4 flex gap-2 flex-wrap">
              <Button
                variant={activeFilter === 'todas' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('todas')}
              >
                Todas ({contadores.todas})
              </Button>
              <Button
                variant={activeFilter === 'classificadas' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('classificadas')}
              >
                Classificadas ({contadores.classificadas})
              </Button>
              <Button
                variant={activeFilter === 'base_parcelas' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('base_parcelas')}
              >
                Base Parcelas ({contadores.baseParcelas})
              </Button>
              <Button
                variant={activeFilter === 'base_padroes' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('base_padroes')}
              >
                Base Padrões ({contadores.basePadroes})
              </Button>
              <Button
                variant={activeFilter === 'journal_entries' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('journal_entries')}
              >
                Journal Entries ({contadores.journalEntries})
              </Button>
              <Button
                variant={activeFilter === 'regras_genericas' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('regras_genericas')}
              >
                Regras Genéricas ({contadores.regrasGenericas})
              </Button>
              <Button
                variant={activeFilter === 'nao_classificadas' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setActiveFilter('nao_classificadas')}
              >
                Não Classificadas ({contadores.naoClassificadas})
              </Button>
              {contadores.duplicadas > 0 && (
                <Button
                  variant={activeFilter === 'duplicadas' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setActiveFilter('duplicadas')}
                >
                  Duplicadas ({contadores.duplicadas})
                </Button>
              )}
            </div>

            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[100px]">Data</TableHead>
                    <TableHead>Lançamento</TableHead>
                    <TableHead className="w-[180px]">Grupo</TableHead>
                    <TableHead className="w-[180px]">Subgrupo</TableHead>
                    <TableHead className="w-[120px]">Origem</TableHead>
                    <TableHead className="text-right w-[120px]">Valor</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRegistros.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center text-muted-foreground">
                        Nenhum registro encontrado
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredRegistros.map((registro) => (
                      <TableRow key={registro.id}>
                        <TableCell className="font-mono text-sm">
                          {registro.data}
                        </TableCell>
                        <TableCell>
                          <div className="flex flex-col">
                            <span className="font-medium">{registro.lancamento}</span>
                            <span className="text-xs text-muted-foreground">
                              {registro.banco} • {registro.cartao}
                            </span>
                            {registro.marcacao_ia && (
                              <span className="text-xs text-blue-600 mt-1">
                                💡 {registro.marcacao_ia}
                              </span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Select
                            value={registro.grupo || ''}
                            onValueChange={(value) => handleGrupoChange(registro.id, value)}
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Selecione grupo">
                                {registro.grupo || 'Selecione grupo'}
                              </SelectValue>
                            </SelectTrigger>
                            <SelectContent>
                              {gruposSubgrupos.grupos.map((grupo) => (
                                <SelectItem key={grupo} value={grupo}>
                                  {grupo}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Select
                            value={registro.subgrupo || ''}
                            onValueChange={(value) => handleSubgrupoChange(registro.id, value)}
                            disabled={!registro.grupo}
                          >
                            <SelectTrigger className="w-full">
                              <SelectValue placeholder="Selecione subgrupo">
                                {registro.subgrupo || 'Selecione subgrupo'}
                              </SelectValue>
                            </SelectTrigger>
                            <SelectContent>
                              {registro.grupo && gruposSubgrupos.subgruposPorGrupo[registro.grupo]?.map((subgrupo) => (
                                <SelectItem key={subgrupo} value={subgrupo}>
                                  {subgrupo}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </TableCell>
                        <TableCell>
                          <Badge variant={
                            registro.origem_classificacao === 'Manual' ? 'default' :
                            registro.origem_classificacao === 'Base Padrões' ? 'secondary' :
                            registro.origem_classificacao === 'Regras Genéricas' ? 'outline' :
                            'secondary'
                          } className="text-xs">
                            {registro.origem_classificacao || 'N/A'}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <span className={registro.valor < 0 ? "text-red-600" : "text-green-600"}>
                            {formatCurrency(registro.valor)}
                          </span>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Actions Inferior */}
        <div className="flex justify-end gap-4">
          <Button onClick={handleCancel} variant="outline" size="lg">
            <X className="mr-2 h-4 w-4" />
            Cancelar Importação
          </Button>
          <Button 
            onClick={handleConfirm} 
            size="lg"
            disabled={isConfirming || registros.length === 0 || contadores.naoClassificadas > 0}
            className={contadores.naoClassificadas > 0 ? 'opacity-50 cursor-not-allowed' : ''}
          >
            {isConfirming ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Processando...
              </>
            ) : contadores.naoClassificadas > 0 ? (
              <>
                <X className="mr-2 h-4 w-4" />
                Aguardando Classificação
              </>
            ) : (
              <>
                <Check className="mr-2 h-4 w-4" />
                Confirmar Importação ({contadores.validas} transações)
              </>
            )}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  )
}
