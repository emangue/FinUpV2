'use client'

/**
 * Transactions Mobile - Tela de Transações
 * 
 * Query params: year, month, grupo, subgrupo, from
 * - from=metas: veio da tela de metas, voltar leva para /mobile/budget
 */

import * as React from 'react'
import { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { format } from 'date-fns'
import { Plus } from 'lucide-react'
import { MonthScrollPicker } from '@/components/mobile/month-scroll-picker'
import { TransactionCard } from '@/components/mobile/transaction-card'
import { MobileHeader } from '@/components/mobile/mobile-header'
import { fetchWithAuth } from '@/core/utils/api-client'
import { API_CONFIG } from '@/core/config/api.config'
import { cn } from '@/lib/utils'
import type { CategoryType } from '@/components/mobile/category-icon'
import { TransactionDetailBottomSheet } from '@/components/mobile/transaction-detail-bottom-sheet'

type FilterType = 'all' | 'receita' | 'despesa'

function grupoToCategory(grupo: string | undefined): CategoryType {
  if (!grupo) return 'outros'
  const g = grupo.toLowerCase()
  if (g.includes('casa') || g.includes('moradia') || g.includes('aluguel')) return 'casa'
  if (g.includes('aliment') || g.includes('restaurante')) return 'alimentacao'
  if (g.includes('compra') || g.includes('shopping')) return 'compras'
  if (g.includes('transporte') || g.includes('combust')) return 'transporte'
  if (g.includes('conta') || g.includes('utilidade')) return 'contas'
  if (g.includes('lazer') || g.includes('saúde') || g.includes('viagem')) return 'lazer'
  return 'outros'
}

interface Transaction {
  id: number
  IdTransacao: string
  Estabelecimento: string
  Valor: number
  Data: string
  GRUPO?: string
  SUBGRUPO?: string
  Grupo?: string
  Subgrupo?: string
  CategoriaGeral?: string
  IdParcela?: string
  origem_classificacao?: string
  MesFatura?: string
  NomeCartao?: string
}

function TransactionsMobileContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const fromMetas = searchParams.get('from') === 'metas'
  const urlGoalId = searchParams.get('goalId')
  const urlYear = searchParams.get('year')
  const urlMonth = searchParams.get('month')
  const urlGrupo = searchParams.get('grupo')
  const urlSubgrupo = searchParams.get('subgrupo')

  const [selectedMonth, setSelectedMonth] = React.useState<Date>(() => {
    if (urlYear && urlMonth) {
      return new Date(parseInt(urlYear), parseInt(urlMonth) - 1, 1)
    }
    return new Date()
  })
  const [filterType, setFilterType] = React.useState<FilterType>(urlGrupo ? 'despesa' : 'all')
  const [transactions, setTransactions] = React.useState<Transaction[]>([])
  const [loading, setLoading] = React.useState(true)
  const [selectedTransaction, setSelectedTransaction] = React.useState<Transaction | null>(null)
  const [detailSheetOpen, setDetailSheetOpen] = React.useState(false)

  React.useEffect(() => {
    fetchTransactions()
  }, [selectedMonth, filterType, urlGrupo, urlSubgrupo])
  
  const fetchTransactions = async () => {
    try {
      setLoading(true)
      
      const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`
      
      const year = format(selectedMonth, 'yyyy')
      const month = format(selectedMonth, 'M')
      
      let url = `${BASE_URL}/transactions/list?year=${year}&month=${month}&limit=100`
      
      if (filterType !== 'all') {
        url += `&categoria_geral=${filterType === 'receita' ? 'Receita' : 'Despesa'}`
      }
      if (urlGrupo) url += `&grupo=${encodeURIComponent(urlGrupo)}`
      if (urlSubgrupo) {
        if (urlSubgrupo === '__null__') {
          url += '&subgrupo_null=1'
        } else {
          url += `&subgrupo=${encodeURIComponent(urlSubgrupo)}`
        }
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
        title={urlGrupo ? `${urlGrupo}${urlSubgrupo && urlSubgrupo !== '__null__' ? ` › ${urlSubgrupo}` : ''}` : 'Transações'}
        leftAction={fromMetas ? 'back' : null}
        onBack={fromMetas ? () => {
          const mes = urlYear && urlMonth ? `?mes=${urlYear}-${String(urlMonth).padStart(2, '0')}` : ''
          const target = urlGoalId ? `/mobile/budget/${urlGoalId}${mes}` : `/mobile/budget${mes}`
          router.push(target)
        } : undefined}
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
                id={transaction.id}
                description={transaction.Estabelecimento}
                amount={transaction.Valor}
                date={transaction.Data}
                group={typeof transaction.GRUPO === 'string' ? transaction.GRUPO : (typeof transaction.Grupo === 'string' ? transaction.Grupo : undefined)}
                subgroup={typeof transaction.SUBGRUPO === 'string' ? transaction.SUBGRUPO : (typeof transaction.Subgrupo === 'string' ? transaction.Subgrupo : undefined)}
                category={grupoToCategory(typeof transaction.GRUPO === 'string' ? transaction.GRUPO : (typeof transaction.Grupo === 'string' ? transaction.Grupo : undefined))}
                onClick={() => {
                  setSelectedTransaction(transaction)
                  setDetailSheetOpen(true)
                }}
              />
            ))}
          </div>
        )}
      </div>
      
      <TransactionDetailBottomSheet
        isOpen={detailSheetOpen}
        onClose={() => {
          setDetailSheetOpen(false)
          setSelectedTransaction(null)
        }}
        transaction={selectedTransaction}
        onSaved={fetchTransactions}
      />

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

export default function TransactionsMobilePage() {
  return (
    <Suspense fallback={
      <div className="flex flex-col h-screen bg-gray-50 items-center justify-center">
        <div className="text-gray-500">Carregando...</div>
      </div>
    }>
      <TransactionsMobileContent />
    </Suspense>
  )
}
