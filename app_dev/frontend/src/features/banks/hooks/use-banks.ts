"use client"

import { useState, useEffect, useCallback } from 'react'
import { fetchWithAuth } from '@/core/utils/api-client'  // ✅ FASE 3 - Autenticação obrigatória
import { BankCompatibility, BankCreate, BankUpdate } from '../types'
import * as bankApi from '../services/bank-api'
import { getCached, setCached, getInFlight, setInFlight, invalidateCache } from '@/core/utils/in-memory-cache'

const BANKS_CACHE_KEY = 'banks:list'
const BANKS_TTL = 5 * 60 * 1000

export function useBanks() {
  const [banks, setBanks] = useState<BankCompatibility[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBanks = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const cached = getCached<BankCompatibility[]>(BANKS_CACHE_KEY)
      if (cached) {
        setBanks(cached)
        return
      }

      let inFlight = getInFlight<{ banks: BankCompatibility[] }>(BANKS_CACHE_KEY)
      if (!inFlight) {
        inFlight = bankApi.fetchBanks()
        setInFlight(BANKS_CACHE_KEY, inFlight)
      }

      const data = await inFlight
      const list = data.banks || []
      setCached(BANKS_CACHE_KEY, list, BANKS_TTL)
      setBanks(list)
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
      invalidateCache('banks:')
      await fetchBanks()
      return newBank
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao criar banco'
      setError(message)
      throw err
    }
  }, [fetchBanks])

  const updateBank = useCallback(async (id: number, data: BankUpdate) => {
    try {
      const response = await fetchWithAuth(`/api/v1/compatibility/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Erro ao atualizar')
      }

      invalidateCache('banks:')
      await fetchBanks()
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao atualizar banco'
      setError(message)
      throw err
    }
  }, [fetchBanks])

  const deleteBank = useCallback(async (id: number) => {
    try {
      await bankApi.deleteBank(id)
      invalidateCache('banks:')
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
