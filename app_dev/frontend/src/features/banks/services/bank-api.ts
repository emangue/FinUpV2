import { BankCompatibility, BankCreate, BankUpdate, BankResponse } from '../types'

export async function fetchBanks(): Promise<BankResponse> {
  const response = await fetch('/api/compatibility')
  if (!response.ok) {
    throw new Error(`Erro ao buscar bancos: ${response.statusText}`)
  }
  return response.json()
}

export async function createBank(data: BankCreate): Promise<BankCompatibility> {
  const response = await fetch('/api/compatibility', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      bank_name: data.bank_name,
      file_format: Object.keys(data.formats)[0], // Por enquanto, criar apenas o primeiro formato
      status: Object.values(data.formats)[0]
    })
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Erro ao criar banco')
  }
  
  return response.json()
}

export async function updateBank(id: number, data: { status: 'OK' | 'WIP' | 'TBD' }): Promise<BankCompatibility> {
  const response = await fetch(`/api/compatibility/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Erro ao atualizar banco')
  }
  
  return response.json()
}

export async function deleteBank(id: number): Promise<void> {
  const response = await fetch(`/api/compatibility/${id}`, {
    method: 'DELETE'
  })
  
  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'Erro ao excluir banco')
  }
}
