"use client"

import * as React from "react"
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

interface Transaction {
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
  const [activeTab, setActiveTab] = React.useState("all")
  const [transactions, setTransactions] = React.useState<Transaction[]>([])
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
  const [selectedTransaction, setSelectedTransaction] = React.useState<Transaction | null>(null)

  const fetchFilteredTotal = async (type: string, filters: FilterValues = {}) => {
    try {
      const params = new URLSearchParams()

      // Aplicar os mesmos filtros da listagem
      if (type !== 'all') {
        if (type === 'Receita') {
          params.set('tipo_transacao', 'Receitas')
        } else if (type === 'Despesa') {
          params.set('tipo_transacao', 'Despesas')
        } else if (type === 'Investimentos') {
          params.set('grupo', 'Investimentos')
        } else if (type === 'Transferência Entre Contas') {
          params.set('tipo_gasto', 'Transferência Entre Contas')
        }
      }

      // Adicionar filtros
      if (filters.estabelecimento) params.append('estabelecimento', filters.estabelecimento)
      if (filters.grupo) params.append('grupo', filters.grupo)
      if (filters.subgrupo) params.append('subgrupo', filters.subgrupo)
      if (filters.tipoGasto) params.append('tipo_gasto', filters.tipoGasto)
      if (filters.banco) params.append('search', filters.banco)

      const response = await fetch(`/api/transactions/filtered-total?${params.toString()}`)
      if (response.ok) {
        const data = await response.json()
        setSomaTotal(data.total_filtrado || 0)
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
          params.set('tipo_transacao', 'Receitas')
        } else if (type === 'Despesa') {
          params.set('tipo_transacao', 'Despesas')
        } else if (type === 'Investimentos') {
          params.set('grupo', 'Investimentos')
        } else if (type === 'Transferência Entre Contas') {
          params.set('tipo_gasto', 'Transferência Entre Contas')
        }
      }

      // Adicionar filtros à query
      if (filters.estabelecimento) params.append('estabelecimento', filters.estabelecimento)
      if (filters.grupo) params.append('grupo', filters.grupo)
      if (filters.subgrupo) params.append('subgrupo', filters.subgrupo)
      if (filters.tipoGasto) params.append('tipo_gasto', filters.tipoGasto)
      if (filters.banco) params.append('search', filters.banco) // Use search para banco
      if (filters.mesInicio || filters.mesFim) {
        // Se tiver filtros de mês, pode precisar de lógica adicional
      }

      const response = await fetch(`/api/transactions/list?${params.toString()}`)
      
      if (response.ok) {
        const data = await response.json()
        setTransactions(data.transactions || [])
        setPagination({
          page: data.pagination?.page || 1,
          limit: data.pagination?.limit || 10,
          total: data.pagination?.total || 0,
          totalPages: data.pagination?.total_pages || 0
        })
        // Não calcular soma aqui, será calculada pela nova API
        // const soma = (data.transactions || []).reduce((acc: number, t: Transaction) => acc + t.Valor, 0)
        // setSomaTotal(soma)
      }
    } catch (error) {
      console.error('Erro ao buscar transações:', error)
    } finally {
      setLoading(false)
    }
  }

  React.useEffect(() => {
    fetchTransactions(activeTab, 1, appliedFilters)
    fetchFilteredTotal(activeTab, appliedFilters)
  }, [activeTab])

  const handleTabChange = (value: string) => {
    setActiveTab(value)
  }

  const handlePageChange = (newPage: number) => {
    fetchTransactions(activeTab, newPage, appliedFilters)
  }

  const handleApplyFilters = (filters: FilterValues) => {
    setAppliedFilters(filters)
    fetchTransactions(activeTab, 1, filters)
    fetchFilteredTotal(activeTab, filters)
  }

  const handleTransactionClick = (transaction: Transaction) => {
    setSelectedTransaction(transaction)
    setEditModalOpen(true)
  }

  const handleToggleIgnorar = async (transaction: Transaction, checked: boolean) => {
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
      
      // Recarregar totais após mudança
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
                      <div className="text-sm text-muted-foreground">
                        Mostrando {Math.min((pagination.page - 1) * pagination.limit + 1, pagination.total)} a{' '}
                        {Math.min(pagination.page * pagination.limit, pagination.total)} de {pagination.total} transações
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
          transaction={selectedTransaction}
          onSave={() => fetchTransactions(activeTab, pagination.page, appliedFilters)}
        />
      </div>
    </DashboardLayout>
  )
}