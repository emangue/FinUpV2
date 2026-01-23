'use client'

import React, { useState, useEffect } from 'react'
import { fetchWithAuth } from '@/core/utils/api-client'
import { TransactionsMobileHeader } from '@/features/transactions/components/mobile/transactions-header'
import { MonthFilterMobile } from '@/features/transactions/components/mobile/month-filter'
import { TransactionsList } from '@/features/transactions/components/mobile/transactions-list'

interface Transaction {
  id: string
  data: string
  lancamento: string
  grupo: string
  valor: number
  tipo: string
}

export default function TransactionsMobilePage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  const currentDate = new Date()
  const [selectedYear, setSelectedYear] = useState(String(currentDate.getFullYear()))
  const [selectedMonth, setSelectedMonth] = useState(String(currentDate.getMonth() + 1).padStart(2, '0'))
  const [filterType, setFilterType] = useState<'all' | 'receitas' | 'despesas'>('all')

  const fetchTransactions = async (year: string, month: string, type: string) => {
    try {
      setLoading(true)
      setError(null)
      
      const apiUrl = process.env.NEXT_PUBLIC_BACKEND_URL 
        ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1` 
        : 'http://localhost:8000/api/v1'
      
      const params = new URLSearchParams({ 
        year, 
        month,
        limit: '100'
      })
      
      if (type !== 'all') {
        params.append('tipo', type === 'receitas' ? 'Receita' : 'Despesa')
      }
      
      const response = await fetchWithAuth(`${apiUrl}/transactions/list?${params}`)
      
      if (!response.ok) {
        throw new Error(`Erro ao buscar transações: ${response.statusText}`)
      }
      
      const data = await response.json()
      setTransactions(data.transactions || [])
      
    } catch (error) {
      console.error('Error fetching transactions:', error)
      setError(error instanceof Error ? error.message : 'Erro desconhecido')
    } finally {
      setLoading(false)
    }
  }

  const handleMonthChange = (month: string, year: string) => {
    setSelectedMonth(month)
    setSelectedYear(year)
    fetchTransactions(year, month, filterType)
  }

  const handleFilterChange = (type: 'all' | 'receitas' | 'despesas') => {
    setFilterType(type)
    fetchTransactions(selectedYear, selectedMonth, type)
  }

  useEffect(() => {
    fetchTransactions(selectedYear, selectedMonth, filterType)
  }, [])

  return (
    <div className="min-h-screen bg-background pb-20">
      {/* Header fixo */}
      <TransactionsMobileHeader />

      {/* Conteúdo com padding top para compensar header e bottom nav */}
      <div className="pt-16 pb-6">
        {/* Filtros de mês e tipo */}
        <div className="px-4 mb-4">
          <MonthFilterMobile
            selectedYear={selectedYear}
            selectedMonth={selectedMonth}
            filterType={filterType}
            onMonthChange={handleMonthChange}
            onFilterChange={handleFilterChange}
          />
        </div>

        {/* Lista de transações */}
        <TransactionsList
          transactions={transactions}
          loading={loading}
          error={error}
        />
      </div>
    </div>
  )
}
