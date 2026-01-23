import { fetchWithAuth } from '@/core/utils/api-client';  // ✅ FASE 3 - Autenticação obrigatória
import { Category, CategoryCreate, CategoryUpdate, CategoryResponse } from '../types'

export async function fetchCategories(): Promise<CategoryResponse> {
  const response = await fetchWithAuth('/api/v1/categories')
  if (!response.ok) {
    throw new Error(`Erro ao buscar categorias: ${response.statusText}`)
  }
  return response.json()
}

export async function createCategory(data: CategoryCreate): Promise<Category> {
  const response = await fetchWithAuth('/api/v1/categories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao criar categoria: ${response.statusText}`)
  }
  
  return response.json()
}

export async function updateCategory(id: number, data: CategoryUpdate): Promise<Category> {
  const response = await fetchWithAuth(`/api/v1/categories/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao atualizar categoria: ${response.statusText}`)
  }
  
  return response.json()
}

export async function deleteCategory(id: number): Promise<void> {
  const response = await fetchWithAuth(`/api/v1/categories/${id}`, {
    method: 'DELETE'
  })
  
  if (!response.ok) {
    throw new Error(`Erro ao excluir categoria: ${response.statusText}`)
  }
}
