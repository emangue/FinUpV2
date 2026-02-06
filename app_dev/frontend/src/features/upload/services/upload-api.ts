/**
 * Upload API Services
 * Conecta componentes de upload com APIs reais do backend
 */

import { API_CONFIG } from '@/core/config/api.config';
import { Bank, CreditCard } from '../types';

const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`;

/**
 * Lista todos os bancos disponíveis para upload
 */
export async function fetchBanks(): Promise<Bank[]> {
  const response = await fetch(`${BASE_URL}/compatibility/banks`);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar instituições financeiras');
  }
  
  const data = await response.json();
  
  // Converter formato da API para formato do componente
  return data.banks.map((bank: any) => ({
    id: bank.nome, // Usar nome como ID
    name: bank.nome,
    formats: bank.formatos_suportados || []
  }));
}

/**
 * Lista todos os cartões de crédito do usuário
 */
export async function fetchCreditCards(): Promise<CreditCard[]> {
  const response = await fetch(`${BASE_URL}/cards`, {
    headers: {
      'Content-Type': 'application/json',
      // TODO: Adicionar token de autenticação quando implementado
      // 'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Erro ao buscar cartões de crédito');
  }
  
  const data = await response.json();
  
  // Converter formato da API para formato do componente
  return data.map((card: any) => ({
    id: card.id.toString(),
    name: `${card.banco_nome} - ${card.numero_final}`,
    bank: card.banco_nome,
    lastDigits: card.numero_final
  }));
}

/**
 * Faz upload de arquivo e retorna sessionId
 */
export async function uploadFile(formData: {
  file: File;
  banco: string;
  tipo: 'extrato' | 'fatura';
  cartaoId?: string;
  mes?: string;
  ano?: number;
  formato: string;
}): Promise<{ sessionId: string }> {
  const body = new FormData();
  body.append('file', formData.file);
  body.append('banco', formData.banco);
  body.append('tipo_documento', formData.tipo);
  body.append('formato', formData.formato);
  
  if (formData.tipo === 'fatura' && formData.cartaoId) {
    body.append('cartao_id', formData.cartaoId);
  }
  
  if (formData.mes && formData.ano) {
    body.append('mes', formData.mes);
    body.append('ano', formData.ano.toString());
  }
  
  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    body,
    headers: {
      // TODO: Adicionar token de autenticação quando implementado
      // 'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Erro ao fazer upload do arquivo');
  }
  
  const data = await response.json();
  return { sessionId: data.session_id || data.sessionId };
}
