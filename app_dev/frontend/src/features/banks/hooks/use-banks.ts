"use client"

import { useState, useEffect, useCallback } from 'react'
import { BankCompatibility, BankCreate, BankUpdate } from '../types'
import * as bankApi from '../services/bank-api'

export function useBanks() {
  const [banks, setBanks] = useState<BankCompatibility[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBanks = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await bankApi.fetchBanks()
      setBanks(data.banks || [])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro desconhecido'
      setError(message)
      console.error('[useBanks] Erro ao buscar:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const createBank = useCallback(async (data: BankCreate) => {
    try {
      const newBank = await bankApi.createBank(data)
      await fetchBanks() // Recarregar lista
      return newBank
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao criar banco'
      setError(message)
      throw err
    }
  }, [fetchBanks])

  const updateBank = useCallback(async (id: number, data: BankUpdate) => {
    try {
      const response = await fetch(`/api/compatibility/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erro ao atualizar')
      }
      
      await fetchBanks() // Recarregar lista
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao atualizar banco'
      setError(message)
      throw err
    }
  }, [fetchBanks])

  const deleteBank = useCallback(async (id: number) => {
    try {
      await bankApi.deleteBank(id)
      setBanks(prev => prev.filter(bank => bank.id !== id))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao excluir banco'
      setError(message)
      throw err
    }
  }, [])

  useEffect(() => {
    fetchBanks()
  }, [fetchBanks])

  return {
    banks,
    loading,
    error,
    fetchBanks,
    refetch: fetchBanks,
    createBank,
    updateBank,
    deleteBank
  }
}
