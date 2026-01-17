"use client"

import * as React from "react"
import { Suspense } from "react"
import { useSearchParams } from "next/navigation"
import DashboardLayout from "@/components/dashboard-layout"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  ChevronLeft,
  ChevronRight,
  Search,
  Filter,
  Download,
} from "lucide-react"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { TransactionFilters, FilterValues } from "@/features/transactions/components/transaction-filters"
import { EditTransactionModal } from "@/features/transactions"

interface TransactionData {
  IdTransacao: string
  Data: string
  Estabelecimento: string
  Valor: number
  ValorPositivo: number
  TipoTransacao: string
  GRUPO: string
  SUBGRUPO: string
  TipoGasto: string
  origem_classificacao: string
  MesFatura: string
  banco_origem: string
  NomeCartao: string
  CategoriaGeral: string
  IgnorarDashboard: number
}

interface PaginationInfo {
  page: number
  limit: number
  total: number
  totalPages: number
}

export default function TransactionsPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Carregando...</div>}>
      <TransactionsPageContent />
    </Suspense>
  )
}

function TransactionsPageContent() {
  const searchParams = useSearchParams()
  const [activeTab, setActiveTab] = React.useState("all")
  const [transactions, setTransactions] = React.useState<TransactionData[]>([])
  const [pagination, setPagination] = React.useState<PaginationInfo>({
    page: 1,
    limit: 10,
    total: 0,
    totalPages: 0
  })
  const [loading, setLoading] = React.useState(true)
  const [searchTerm, setSearchTerm] = React.useState("")
  const [filtersOpen, setFiltersOpen] = React.useState(false)
  const [appliedFilters, setAppliedFilters] = React.useState<FilterValues>({})
  const [somaTotal, setSomaTotal] = React.useState(0)
  const [editModalOpen, setEditModalOpen] = React.useState(false)
  const [selectedTransaction, setSelectedTransaction] = React.useState<TransactionData | null>(null)
  const [isInitialized, setIsInitialized] = React.useState(false)

  // Aplicar filtros de query params sempre que mudarem
  React.useEffect(() => {
    const initialFilters: FilterValues = {}
    
    // getAll para pegar múltiplos valores de tipo_gasto
    const tiposGasto = searchParams.getAll('tipo_gasto')
    const year = searchParams.get('year')
    const month = searchParams.get('month')
    const mesReferencia = searchParams.get('mes_referencia')
    const grupo = searchParams.get('grupo')
    const subgrupo = searchParams.get('subgrupo')
    const estabelecimento = searchParams.get('estabelecimento')
    const cartao = searchParams.get('cartao')
    
    // Se tiver múltiplos tipos, juntar com vírgula para passar no filtro
    if (tiposGasto.length > 0) {
      initialFilters.tipoGasto = tiposGasto.join(',')
    }
    
    // Se vier year e month da dashboard, converter para mes_referencia
    if (year && month) {
      const mesRef = `${year}-${month.padStart(2, '0')}`
      initialFilters.mesInicio = mesRef
      initialFilters.mesFim = mesRef
    } else if (year) {
      // Se tiver só year (todos os meses), filtrar o ano inteiro
      initialFilters.mesInicio = `${year}-01`
      initialFilters.mesFim = `${year}-12`
    } else if (mesReferencia) {
      // mes_referencia vem no formato YYYYMM, converter para YYYY-MM
      const ano = mesReferencia.substring(0, 4)
      const mes = mesReferencia.substring(4, 6)
      const mesFormatado = `${ano}-${mes}`
      initialFilters.mesInicio = mesFormatado
      initialFilters.mesFim = mesFormatado
    }
    
    if (grupo) initialFilters.grupo = grupo
    if (subgrupo) initialFilters.subgrupo = subgrupo
    if (estabelecimento) initialFilters.estabelecimento = estabelecimento
    if (cartao) initialFilters.cartao = cartao
    
    if (Object.keys(initialFilters).length > 0) {
      setAppliedFilters(initialFilters)
      setFiltersOpen(false)
      setIsInitialized(true)
      
      // Disparar fetch imediatamente com os filtros
      fetchTransactions(activeTab, 1, initialFilters)
      fetchFilteredTotal(activeTab, initialFilters)
    } else {
      setIsInitialized(true)
      // Buscar sem filtros se não houver query params
      fetchTransactions(activeTab, 1, {})
      fetchFilteredTotal(activeTab, {})
    }
  }, [searchParams])

  React.useEffect(() => {
    // Se ainda não inicializou, espera
    if (!isInitialized) return
    
    fetchTransactions(activeTab, 1, appliedFilters)
    fetchFilteredTotal(activeTab, appliedFilters)
  }, [activeTab, appliedFilters, isInitialized])

  const fetchFilteredTotal = async (type: string, filters: FilterValues = {}) => {
    try {
      const params = new URLSearchParams()

      // Aplicar os mesmos filtros da listagem
      if (type !== 'all') {
        if (type === 'Receita') {
          params.set('categoria_geral', 'Receita')
        } else if (type === 'Despesa') {
          params.set('categoria_geral', 'Despesa')
        } else if (type === 'Investimentos') {
          params.set('categoria_geral', 'Investimentos')
        } else if (type === 'Transferência Entre Contas') {
          params.set('categoria_geral', 'Transferência')
        }
      } else if (filters.cartao) {
        // Se tem filtro de cartão, sempre é Despesa
        params.set('categoria_geral', 'Despesa')
      }

      // Adicionar filtros
      if (filters.estabelecimento) params.append('estabelecimento', filters.estabelecimento)
      if (filters.grupo) params.append('grupo', filters.grupo)
      if (filters.subgrupo) params.append('subgrupo', filters.subgrupo)
      if (filters.tipoGasto) {
        // Se tiver múltiplos tipos separados por vírgula, adicionar cada um
        const tipos = filters.tipoGasto.split(',').map(t => t.trim()).filter(t => t)
        tipos.forEach(tipo => params.append('tipo_gasto', tipo))
      }
      if (filters.banco) params.append('search', filters.banco)
      if (filters.cartao) params.append('cartao', filters.cartao)
      
      // Converter mesInicio/mesFim (formato "YYYY-MM") para year e month
      if (filters.mesInicio) {
        const [year, month] = filters.mesInicio.split('-')
        if (year) {
          params.append('year', year)
          // Só adicionar month se mesInicio e mesFim forem iguais (mês específico)
          if (month && filters.mesInicio === filters.mesFim) {
            params.append('month', month)
          }
        }
      }

      const response = await fetch(`/api/transactions/filtered-total?${params.toString()}`)
      if (response.ok) {
        const data = await response.json()
        setSomaTotal(data.total || 0)
      }
    } catch (error) {
      console.error('Erro ao buscar total filtrado:', error)
    }
  }

  const fetchTransactions = async (type: string, page: number = 1, filters: FilterValues = {}) => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: page.toString(),
        limit: pagination.limit.toString(),
      })

      // Adicionar categoria geral baseada no activeTab
      if (type !== 'all') {
        if (type === 'Receita') {
          params.set('categoria_geral', 'Receita')
        } else if (type === 'Despesa') {
          params.set('categoria_geral', 'Despesa')
        } else if (type === 'Investimentos') {
          params.set('categoria_geral', 'Investimentos')
        } else if (type === 'Transferência Entre Contas') {
          params.set('categoria_geral', 'Transferência')
        }
      }

      // Adicionar filtros à query
      if (filters.estabelecimento) params.append('estabelecimento', filters.estabelecimento)
      if (filters.grupo) params.append('grupo', filters.grupo)
      if (filters.subgrupo) params.append('subgrupo', filters.subgrupo)
      if (filters.tipoGasto) {
        // Se tiver múltiplos tipos separados por vírgula, adicionar cada um
        const tipos = filters.tipoGasto.split(',').map(t => t.trim()).filter(t => t)
        tipos.forEach(tipo => params.append('tipo_gasto', tipo))
      }
      if (filters.banco) params.append('search', filters.banco) // Use search para banco
      if (filters.cartao) params.append('cartao', filters.cartao)
      
      // Converter mesInicio/mesFim (formato "YYYY-MM") para year e month
      if (filters.mesInicio) {
        const [year, month] = filters.mesInicio.split('-')
        if (year) {
          params.append('year', year)
          // Só adicionar month se mesInicio e mesFim forem iguais (mês específico)
          if (month && filters.mesInicio === filters.mesFim) {
            params.append('month', month)
          }
        }
      }

      const response = await fetch(`/api/transactions/list?${params.toString()}`)
      
      if (response.ok) {
        const data = await response.json()
        setTransactions(data.transactions || [])
        
        // API retorna total, page, limit diretamente (não dentro de pagination)
        const total = data.total || 0
        const page = data.page || 1
        const limit = data.limit || 10
        const totalPages = Math.ceil(total / limit)
        
        setPagination({
          page,
          limit,
          total,
          totalPages
        })
      }
    } catch (error) {
      console.error('Erro ao buscar transações:', error)
    } finally {
      setLoading(false)
    }
  }

  // Adapter para converter TransactionData para Transaction do modal
  const adaptTransactionForModal = (transactionData: TransactionData | null) => {
    if (!transactionData) return null
    return {
      ...transactionData,
      Grupo: transactionData.GRUPO,
      SubGrupo: transactionData.SUBGRUPO,
    }
  }

  const handleTabChange = (value: string) => {
    setActiveTab(value)
  }

  const handlePageChange = (newPage: number) => {
    fetchTransactions(activeTab, newPage, appliedFilters)
  }

  const handleLimitChange = (newLimit: string) => {
    const limit = parseInt(newLimit)
    const newPagination = { ...pagination, limit, page: 1 }
    setPagination(newPagination)
    
    // Chamar fetchTransactions com o novo limit diretamente
    const fetchWithNewLimit = async () => {
      try {
        setLoading(true)
        const params = new URLSearchParams({
          page: '1',
          limit: newLimit,
        })

        // Adicionar categoria geral baseada no activeTab
        if (activeTab !== 'all') {
          if (activeTab === 'Receita') {
            params.set('categoria_geral', 'Receita')
          } else if (activeTab === 'Despesa') {
            params.set('categoria_geral', 'Despesa')
          } else if (activeTab === 'Investimentos') {
            params.set('categoria_geral', 'Investimentos')
          } else if (activeTab === 'Transferência Entre Contas') {
            params.set('categoria_geral', 'Transferência')
          }
        }

        // Adicionar filtros à query
        if (appliedFilters.estabelecimento) params.append('estabelecimento', appliedFilters.estabelecimento)
        if (appliedFilters.grupo) params.append('grupo', appliedFilters.grupo)
        if (appliedFilters.subgrupo) params.append('subgrupo', appliedFilters.subgrupo)
        if (appliedFilters.tipoGasto) {
          const tipos = appliedFilters.tipoGasto.split(',').map(t => t.trim()).filter(t => t)
          tipos.forEach(tipo => params.append('tipo_gasto', tipo))
        }
        if (appliedFilters.banco) params.append('search', appliedFilters.banco)
        if (appliedFilters.cartao) params.append('cartao', appliedFilters.cartao)
        
        if (appliedFilters.mesInicio) {
          const [year, month] = appliedFilters.mesInicio.split('-')
          if (year) {
            params.append('year', year)
            if (month && appliedFilters.mesInicio === appliedFilters.mesFim) {
              params.append('month', month)
            }
          }
        }

        const response = await fetch(`/api/transactions/list?${params.toString()}`)
        if (response.ok) {
          const data = await response.json()
          setTransactions(data.transactions)
          setPagination({
            page: data.pagination?.page || 1,
            limit: data.pagination?.limit || limit,
            total: data.pagination?.total || 0,
            totalPages: data.pagination?.totalPages || 1
          })
        }
      } catch (error) {
        console.error('Erro ao buscar transações:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchWithNewLimit()
    // Atualizar total filtrado também
    fetchFilteredTotal(activeTab, appliedFilters)
  }

  const handleApplyFilters = (filters: FilterValues) => {
    setAppliedFilters(filters)
    fetchTransactions(activeTab, 1, filters)
    fetchFilteredTotal(activeTab, filters)
  }

  const handleTransactionClick = (transaction: TransactionData) => {
    setSelectedTransaction(transaction)
    setEditModalOpen(true)
  }

  const handleToggleIgnorar = async (transaction: TransactionData, checked: boolean) => {
    const novoValor = checked ? 0 : 1

    // Atualiza otimisticamente para refletir o clique imediato
    setTransactions(prev => prev.map(t =>
      t.IdTransacao === transaction.IdTransacao
        ? { ...t, IgnorarDashboard: novoValor }
        : t
    ))

    try {
      const response = await fetch(`/api/transactions/update/${encodeURIComponent(transaction.IdTransacao)}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ IgnorarDashboard: novoValor })
      })

      if (!response.ok) {
        throw new Error(`Falha no PATCH: ${response.status}`)
      }
      
      // Apenas atualiza o total sem recarregar a lista inteira
      fetchFilteredTotal(activeTab, appliedFilters)
      
    } catch (error) {
      console.error('Erro ao atualizar IgnorarDashboard:', error)
      // Reverte se falhar
      setTransactions(prev => prev.map(t =>
        t.IdTransacao === transaction.IdTransacao
          ? { ...t, IgnorarDashboard: transaction.IgnorarDashboard }
          : t
      ))
    }
  }

  const activeFiltersCount = Object.values(appliedFilters).filter(v => v).length

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const formatDate = (dateString: string) => {
    // Data vem do banco no formato dd/mm/yyyy
    if (dateString && dateString.includes('/')) {
      return dateString
    }
    // Fallback para outros formatos
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    } catch {
      return dateString || 'Data inválida'
    }
  }

  const getTransactionTypeBadge = (type: string) => {
    switch (type) {
      case 'Receitas':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Receita</Badge>
      case 'Despesas':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">Despesa</Badge>
      case 'Cartão de Crédito':
        return <Badge className="bg-blue-100 text-blue-800 hover:bg-blue-100">Cartão</Badge>
      default:
        return <Badge variant="outline">{type}</Badge>
    }
  }

  const getOrigemBadge = (origem: string) => {
    if (origem?.includes('Manual')) {
      return <Badge variant="outline" className="bg-purple-50 text-purple-700">Manual</Badge>
    } else if (origem?.includes('IA') || origem?.includes('Auto')) {
      return <Badge variant="outline" className="bg-blue-50 text-blue-700">IA</Badge>
    }
    return <Badge variant="outline">{origem || 'N/A'}</Badge>
  }

  const filteredTransactions = transactions.filter(t =>
    t.Estabelecimento?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.GRUPO?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    t.SUBGRUPO?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <DashboardLayout>
      <div className="flex flex-1 flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Transações</h1>
            <p className="text-muted-foreground">
              Gerencie e visualize todas as suas transações financeiras
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => setFiltersOpen(true)}>
              <Filter className="mr-2 h-4 w-4" />
              Filtros
              {activeFiltersCount > 0 && (
                <span className="ml-1 rounded-full bg-primary px-1.5 py-0.5 text-xs text-primary-foreground">
                  {activeFiltersCount}
                </span>
              )}
            </Button>
            <Button variant="outline" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Exportar
            </Button>
          </div>
        </div>

        <TransactionFilters
          open={filtersOpen}
          onOpenChange={setFiltersOpen}
          onApplyFilters={handleApplyFilters}
          currentFilters={appliedFilters}
        />

        <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="all">Todas</TabsTrigger>
              <TabsTrigger value="Receita">Receitas</TabsTrigger>
              <TabsTrigger value="Despesa">Despesas</TabsTrigger>
              <TabsTrigger value="Investimentos">Investimentos</TabsTrigger>
              <TabsTrigger value="Transferência Entre Contas">Transferências</TabsTrigger>
            </TabsList>
            
            <div className="flex items-center gap-4">
              <div className="text-sm text-muted-foreground">
                Total: <span className="font-semibold text-foreground">{formatCurrency(somaTotal)}</span>
              </div>
              <div className="relative w-64">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar transações..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
          </div>

          <TabsContent value={activeTab} className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>
                  {activeTab === 'all' && 'Todas as Transações'}
                  {activeTab === 'Receita' && 'Receitas'}
                  {activeTab === 'Despesa' && 'Despesas'}
                  {activeTab === 'Investimentos' && 'Investimentos'}
                  {activeTab === 'Transferência Entre Contas' && 'Transferências Entre Contas'}
                </CardTitle>
                <CardDescription>
                  {pagination.total} transações encontradas
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex justify-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                  </div>
                ) : (
                  <>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Data</TableHead>
                          <TableHead>Estabelecimento</TableHead>
                          <TableHead>Categoria</TableHead>
                          <TableHead>Tipo</TableHead>
                          <TableHead className="text-right">Valor</TableHead>
                          <TableHead>Marcação</TableHead>
                          <TableHead className="text-center">Dashboard</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {filteredTransactions.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                              Nenhuma transação encontrada
                            </TableCell>
                          </TableRow>
                        ) : (
                          filteredTransactions.map((transaction) => (
                            <TableRow 
                              key={transaction.IdTransacao}
                              className="cursor-pointer hover:bg-muted/50"
                              onClick={() => handleTransactionClick(transaction)}
                            >
                              <TableCell className="font-medium">
                                {formatDate(transaction.Data)}
                              </TableCell>
                              <TableCell>
                                <div>
                                  <div className="font-medium">{transaction.Estabelecimento}</div>
                                  <div className="text-sm text-muted-foreground">
                                    {transaction.TipoGasto}
                                  </div>
                                </div>
                              </TableCell>
                              <TableCell>
                                <div>
                                  <div className="font-medium">{transaction.GRUPO}</div>
                                  <div className="text-sm text-muted-foreground">
                                    {transaction.SUBGRUPO}
                                  </div>
                                </div>
                              </TableCell>
                              <TableCell>
                                {getTransactionTypeBadge(transaction.TipoTransacao)}
                              </TableCell>
                              <TableCell className={`text-right font-medium ${transaction.Valor >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatCurrency(transaction.Valor)}
                              </TableCell>
                              <TableCell>
                                {getOrigemBadge(transaction.origem_classificacao)}
                              </TableCell>
                              <TableCell className="text-center" onClick={(e) => e.stopPropagation()}>
                                <div className="flex items-center justify-center">
                                  <Switch
                                    checked={transaction.IgnorarDashboard === 0}
                                    onCheckedChange={(checked) => handleToggleIgnorar(transaction, checked)}
                                  />
                                </div>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>

                    {/* Paginação */}
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-4">
                        <div className="text-sm text-muted-foreground">
                          Mostrando {Math.min((pagination.page - 1) * pagination.limit + 1, pagination.total)} a{' '}
                          {Math.min(pagination.page * pagination.limit, pagination.total)} de {pagination.total} transações
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-muted-foreground">Itens por página:</span>
                          <Select 
                            value={pagination.limit.toString()} 
                            onValueChange={handleLimitChange}
                          >
                            <SelectTrigger className="w-[70px] h-8">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="10">10</SelectItem>
                              <SelectItem value="20">20</SelectItem>
                              <SelectItem value="30">30</SelectItem>
                              <SelectItem value="50">50</SelectItem>
                              <SelectItem value="100">100</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange(pagination.page - 1)}
                          disabled={pagination.page === 1 || loading}
                        >
                          <ChevronLeft className="h-4 w-4" />
                          Anterior
                        </Button>
                        <div className="text-sm">
                          Página {pagination.page} de {pagination.totalPages}
                        </div>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handlePageChange(pagination.page + 1)}
                          disabled={pagination.page === pagination.totalPages || loading}
                        >
                          Próxima
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        <EditTransactionModal
          open={editModalOpen}
          onOpenChange={setEditModalOpen}
          transaction={adaptTransactionForModal(selectedTransaction)}
          onSave={() => fetchTransactions(activeTab, pagination.page, appliedFilters)}
        />
      </div>
    </DashboardLayout>
  )
}