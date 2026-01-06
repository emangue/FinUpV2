"use client"

import { useState, useEffect, useCallback } from 'react'
import { Category, CategoryCreate, CategoryUpdate } from '../types'
import * as categoryApi from '../services/category-api'

export function useCategories() {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await categoryApi.fetchCategories()
      setCategories(data.categories || [])
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
