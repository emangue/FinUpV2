'use client'

/**
 * Transactions Mobile - Tela de Transações
 * 
 * Integra:
 * - MonthScrollPicker (scroll de meses)
 * - TransactionCard (cards de transação)
 * - MobileHeader (header unificado)
 * - Pills de filtro (Todas/Receitas/Despesas)
 * 
 * Baseado no PRD Seção 4.2
 * 
 * Endpoints usados:
 * - GET /api/v1/transactions/list?year=X&month=Y&categoria_geral=X
 */

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { startOfMonth, endOfMonth, format } from 'date-fns'
import { Plus } from 'lucide-react'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { TransactionCard } from '@/components/mobile/transaction-card'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { cn } from '@/lib/utils'

type FilterType = 'all' | 'receita' | 'despesa'

interface Transaction {
  id: number
  Estabelecimento: string
  Valor: number
  Data: string
  Grupo: string
  Subgrupo?: string
  CategoriaGeral: string
}

export default function TransactionsMobilePage() {
  const router = useRouter()
  const [selectedMonth, setSelectedMonth] = React.useState<Date>(new Date())
  const [filterType, setFilterType] = React.useState<FilterType>('all')
  const [transactions, setTransactions] = React.useState<Transaction[]>([])
  const [loading, setLoading] = React.useState(true)
  
  // Buscar transações quando mês ou filtro mudar
  React.useEffect(() => {
    fetchTransactions()
  }, [selectedMonth, filterType])
  
  const fetchTransactions = async () => {
    try {
      setLoading(true)
      
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      
      const year = format(selectedMonth, 'yyyy')
      const month = format(selectedMonth, 'M') // Mês sem zero à esquerda
      
      // Buscar transações usando endpoint correto /list
      let url = `${BASE_URL}/transactions/list?year=${year}&month=${month}&limit=100`
      
      // Adicionar filtro de categoria se não for "all"
      if (filterType !== 'all') {
        url += `&categoria_geral=${filterType === 'receita' ? 'Receita' : 'Despesa'}`
      }
      
      const response = await fetchWithAuth(url)
      
      if (response.status === 401) {
        console.error('Não autenticado. Redirecionando para login...')
        router.push('/login')
        return
      }
      
      if (!response.ok) {
        throw new Error(`Erro ${response.status}: ${response.statusText}`)
      }
      
      const data = await response.json()
      setTransactions(data.transactions || [])
      
    } catch (error) {
      console.error('Erro ao buscar transações:', error)
      setTransactions([])
    } finally {
      setLoading(false)
    }
  }
  
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }
  
  const formatDate = (dateStr: string) => {
    // Data vem como DD/MM/YYYY
    const [day, month] = dateStr.split('/')
    return `${day}/${month}`
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <MobileHeader
        title="Transações"
        showBackButton={false}
      />
      
      {/* Month Picker */}
      <MonthScrollPicker
        selectedMonth={selectedMonth}
        onMonthChange={setSelectedMonth}
        className="bg-white border-b border-gray-200"
      />
      
      {/* Filter Pills */}
      <div className="flex gap-2 px-5 py-3 bg-white border-b border-gray-200">
        <button
          onClick={() => setFilterType('all')}
          className={cn(
            'px-4 py-2 rounded-full text-sm font-medium transition-all',
            filterType === 'all'
              ? 'bg-black text-white shadow-md'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          )}
        >
          Todas
        </button>
        <button
          onClick={() => setFilterType('receita')}
          className={cn(
            'px-4 py-2 rounded-full text-sm font-medium transition-all',
            filterType === 'receita'
              ? 'bg-green-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          )}
        >
          Receitas
        </button>
        <button
          onClick={() => setFilterType('despesa')}
          className={cn(
            'px-4 py-2 rounded-full text-sm font-medium transition-all',
            filterType === 'despesa'
              ? 'bg-red-600 text-white shadow-md'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          )}
        >
          Despesas
        </button>
      </div>
      
      {/* Transactions List */}
      <div className="flex-1 overflow-y-auto p-5">
        {loading ? (
          <div className="flex items-center justify-center py-10">
            <div className="text-gray-500">Carregando...</div>
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10">
            <div className="text-gray-400 text-center mb-4">
              Nenhuma transação neste período.
            </div>
            <button
              onClick={() => router.push('/mobile/upload')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Importar Arquivo
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {transactions.map((transaction) => (
              <TransactionCard
                key={transaction.id}
                description={transaction.Estabelecimento}
                amount={transaction.Valor}
                date={transaction.Data}
                group={transaction.GRUPO}
                subgroup={transaction.SUBGRUPO}
                category={transaction.GRUPO}
                onClick={() => {
                  // TODO: Abrir bottom sheet de detalhes
                  console.log('Clicked transaction:', transaction.id)
                }}
              />
            ))}
          </div>
        )}
      </div>
      
      {/* FAB - Nova Transação */}
      <button
        onClick={() => {
          // TODO: Abrir form de nova transação
          console.log('Nova transação')
        }}
        className="fixed bottom-24 right-5 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg flex items-center justify-center hover:bg-blue-700 transition-all active:scale-95"
        style={{
          boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)'
        }}
        aria-label="Nova transação"
      >
        <Plus className="w-6 h-6" />
      </button>
    </div>
  )
}
