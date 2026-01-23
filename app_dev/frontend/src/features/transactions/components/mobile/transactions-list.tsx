'use client'

import { format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { Card } from '@/components/ui/card'

interface Transaction {
  id: string
  data: string
  lancamento?: string
  grupo?: string
  valor: number
  tipo: string
}

interface TransactionsListProps {
  transactions: Transaction[]
  loading: boolean
  error: string | null
}

// Helper para emoji por categoria
function getEmojiForCategory(categoria: string | undefined): string {
  const emojiMap: { [key: string]: string } = {
    'Alimentação': '🍔',
    'Supermercado': '🛒',
    'Transporte': '🚗',
    'Uber': '🚕',
    'Moradia': '🏠',
    'Aluguel': '🏠',
    'Saúde': '💊',
    'Educação': '📚',
    'Lazer': '🎮',
    'Cinema': '🎬',
    'Vestuário': '👕',
    'Receita': '💰',
    'Salário': '💵',
    'Outros': '📦',
  }
  
  // Verificar se categoria existe
  if (!categoria) return '💳'
  
  // Buscar por match parcial
  const key = Object.keys(emojiMap).find(k => 
    categoria.toLowerCase().includes(k.toLowerCase())
  )
  
  return key ? emojiMap[key] : '💳'
}

// Agrupar transações por data
function groupByDate(transactions: Transaction[]) {
  const groups: { [key: string]: Transaction[] } = {}
  
  transactions.forEach(transaction => {
    const date = transaction.data
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(transaction)
  })
  
  return groups
}

// Formatar data para exibição
function formatDateLabel(dateStr: string): string {
  try {
    // dateStr vem como "DD/MM/YYYY"
    const [day, month, year] = dateStr.split('/')
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
    
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    if (date.toDateString() === today.toDateString()) {
      return 'Hoje'
    }
    if (date.toDateString() === yesterday.toDateString()) {
      return 'Ontem'
    }
    
    return format(date, "d 'de' MMM", { locale: ptBR })
  } catch {
    return dateStr
  }
}

export function TransactionsList({ transactions, loading, error }: TransactionsListProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
    }).format(Math.abs(value))
  }

  if (loading) {
    return (
      <div className="px-4 space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="space-y-2">
            <div className="h-4 w-32 bg-gray-200 animate-pulse rounded" />
            <Card className="p-4">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 bg-gray-200 animate-pulse rounded-full" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-40 bg-gray-200 animate-pulse rounded" />
                  <div className="h-3 w-24 bg-gray-200 animate-pulse rounded" />
                </div>
                <div className="h-5 w-24 bg-gray-200 animate-pulse rounded" />
              </div>
            </Card>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="px-4">
        <Card className="p-6 bg-red-50 border-red-200 text-center">
          <p className="text-sm text-red-600">{error}</p>
        </Card>
      </div>
    )
  }

  if (transactions.length === 0) {
    return (
      <div className="px-4">
        <Card className="p-8 text-center">
          <p className="text-gray-500">Nenhuma transação encontrada</p>
        </Card>
      </div>
    )
  }

  const groupedTransactions = groupByDate(transactions)
  const sortedDates = Object.keys(groupedTransactions).sort((a, b) => {
    const [dayA, monthA, yearA] = a.split('/').map(Number)
    const [dayB, monthB, yearB] = b.split('/').map(Number)
    const dateA = new Date(yearA, monthA - 1, dayA)
    const dateB = new Date(yearB, monthB - 1, dayB)
    return dateB.getTime() - dateA.getTime()
  })

  return (
    <div className="space-y-4">
      {sortedDates.map((date) => (
        <div key={date} className="px-4">
          {/* Header da data */}
          <div className="mb-2">
            <p className="text-sm font-medium text-gray-600">
              {formatDateLabel(date)}
            </p>
          </div>

          {/* Lista de transações do dia */}
          <div className="space-y-2">
            {groupedTransactions[date].map((transaction) => {
              const isReceita = transaction.tipo === 'Receita'
              const emoji = getEmojiForCategory(transaction.grupo)
              
              return (
                <Card key={transaction.id} className="p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3">
                    {/* Emoji/Ícone */}
                    <div className={`h-12 w-12 rounded-full flex items-center justify-center text-2xl ${
                      isReceita ? 'bg-green-100' : 'bg-red-100'
                    }`}>
                      {emoji}
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 truncate">
                        {transaction.grupo || 'Sem categoria'}
                      </p>
                      <p className="text-sm text-gray-500 truncate">
                        {transaction.lancamento || 'Sem descrição'}
                      </p>
                    </div>

                    {/* Valor */}
                    <div className={`text-right font-bold ${
                      isReceita ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {isReceita ? '+ ' : '- '}
                      {formatCurrency(transaction.valor)}
                    </div>
                  </div>
                </Card>
              )
            })}
          </div>
        </div>
      ))}
    </div>
  )
}
