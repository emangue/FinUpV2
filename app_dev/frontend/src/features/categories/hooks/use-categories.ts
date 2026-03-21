"use client"

import { useState, useEffect, useCallback } from 'react'
import { Category, CategoryCreate, CategoryUpdate } from '../types'
import * as categoryApi from '../services/category-api'
import { getCached, setCached, getInFlight, setInFlight, invalidateCache } from '@/core/utils/in-memory-cache'

const CATEGORIES_CACHE_KEY = 'categories:list'
const CATEGORIES_TTL = 5 * 60 * 1000

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)

      const cached = getCached<Category[]>(CATEGORIES_CACHE_KEY)
      if (cached) {
        setCategories(cached)
        return
      }

      let inFlight = getInFlight<{ categories: Category[] }>(CATEGORIES_CACHE_KEY)
      if (!inFlight) {
        inFlight = categoryApi.fetchCategories()
        setInFlight(CATEGORIES_CACHE_KEY, inFlight)
      }

      const data = await inFlight
      const list = data.categories || []
      setCached(CATEGORIES_CACHE_KEY, list, CATEGORIES_TTL)
      setCategories(list)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro desconhecido'
      setError(message)
      console.error('[useCategories] Erro ao buscar:', err)
    } finally {
      setLoading(false)
    }
  }, [])

  const createCategory = useCallback(async (data: CategoryCreate) => {
    try {
      const newCategory = await categoryApi.createCategory(data)
      invalidateCache('categories:')
      setCategories(prev => [...prev, newCategory])
      return newCategory
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao criar categoria'
      setError(message)
      throw err
    }
  }, [])

  const updateCategory = useCallback(async (id: number, data: CategoryUpdate) => {
    try {
      const updated = await categoryApi.updateCategory(id, data)
      invalidateCache('categories:')
      setCategories(prev => prev.map(cat => cat.id === id ? updated : cat))
      return updated
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao atualizar categoria'
      setError(message)
      throw err
    }
  }, [])

  const deleteCategory = useCallback(async (id: number) => {
    try {
      await categoryApi.deleteCategory(id)
      invalidateCache('categories:')
      setCategories(prev => prev.filter(cat => cat.id !== id))
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro ao excluir categoria'
      setError(message)
      throw err
    }
  }, [])

  useEffect(() => {
    fetchCategories()
  }, [fetchCategories])

  return {
    categories,
    loading,
    error,
    refetch: fetchCategories,
    createCategory,
    updateCategory,
    deleteCategory
  }
}
