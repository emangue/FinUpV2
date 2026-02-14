/**
 * Upload API Services
 * Conecta componentes de upload com APIs reais do backend
 */

import { API_CONFIG } from '@/core/config/api.config';
import { fetchWithAuth } from '@/core/utils/api-client';
import { Bank, CreditCard, PreviewData } from '../types';

const BASE_URL = `${API_CONFIG.BACKEND_URL}${API_CONFIG.API_PREFIX}`;

/** Status de compatibilidade por formato (OK=disponível, WIP=em desenvolvimento, TBD=em breve) */
export type FormatStatus = 'OK' | 'WIP' | 'TBD';

/** Mapa banco -> status por formato */
export type BankCompatibilityMap = Record<string, {
  csv_status: FormatStatus;
  excel_status: FormatStatus;
  pdf_status: FormatStatus;
  ofx_status: FormatStatus;
}>;

/**
 * Busca compatibilidade de formatos por banco (usado para desabilitar formatos TBD)
 */
export async function fetchCompatibility(): Promise<BankCompatibilityMap> {
  const response = await fetchWithAuth(`${BASE_URL}/compatibility/`);
  if (!response.ok) {
    return {};
  }
  const data = await response.json();
  const map: BankCompatibilityMap = {};
  for (const item of data.banks || []) {
    map[item.bank_name] = {
      csv_status: item.csv_status || 'TBD',
      excel_status: item.excel_status || 'TBD',
      pdf_status: item.pdf_status || 'TBD',
      ofx_status: item.ofx_status || 'TBD',
    };
  }
  return map;
}

/**
 * Lista todos os bancos disponíveis para upload
 */
export async function fetchBanks(): Promise<Bank[]> {
  const response = await fetchWithAuth(`${BASE_URL}/compatibility/`);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar instituições financeiras');
  }
  
  const data = await response.json();
  
  // Converter formato da API para formato do componente
  return data.banks.map((bank: any) => ({
    id: bank.id?.toString() || bank.bank_name, // Usar ID real do banco
    name: bank.bank_name, // Campo correto da API
    formats: bank.formatos_suportados || []
  }));
}

/**
 * Lista todos os cartões de crédito do usuário
 */
export async function fetchCreditCards(): Promise<CreditCard[]> {
  const response = await fetchWithAuth(`${BASE_URL}/cards/`);
  
  if (!response.ok) {
    throw new Error('Erro ao buscar cartões de crédito');
  }
  
  const data = await response.json();
  
  // API retorna { cards: [...], total: number }
  const cards = data.cards || [];
  
  // Converter formato da API para formato do componente
  return cards.map((card: any) => ({
    id: card.id.toString(),
    bankId: card.banco,
    lastDigits: card.final_cartao,
    name: card.nome_cartao  // ✅ Usar nome_cartao da API
  }));
}

/**
 * Faz upload de arquivo e retorna sessionId
 */
export async function uploadFile(formData: {
  file: File;
  banco: string;
  tipo: 'extrato' | 'fatura';
  cartaoId?: string;  // ID do cartão selecionado
  cartaoNome?: string;  // Nome do cartão
  cartaoFinal?: string;  // Final do cartão
  mes?: string;
  ano?: number;
  formato: string;
}): Promise<{ sessionId: string }> {
  const body = new FormData();
  body.append('file', formData.file);
  body.append('banco', formData.banco);
  body.append('tipoDocumento', formData.tipo);
  
  // Formato em MAIÚSCULO como backend espera (CSV, Excel, PDF, OFX)
  const formatoMap: Record<string, string> = {
    'csv': 'CSV',
    'excel': 'Excel',
    'pdf': 'PDF',
    'pdf-password': 'PDF',
    'ofx': 'OFX'
  };
  body.append('formato', formatoMap[formData.formato] || 'CSV');
  
  // mesFatura é obrigatório no formato YYYY-MM
  if (formData.mes && formData.ano) {
    // Converter "Fevereiro" → "02"
    const monthMap: Record<string, string> = {
      'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
      'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
      'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
    };
    const monthNumber = monthMap[formData.mes] || '01';
    const mesFatura = `${formData.ano}-${monthNumber}`;
    body.append('mesFatura', mesFatura);
  } else {
    // Fallback: usar mês/ano atual
    const now = new Date();
    const mesFatura = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    body.append('mesFatura', mesFatura);
  }
  
  if (formData.tipo === 'fatura' && formData.cartaoNome) {
    // Backend espera nome do cartão (não ID)
    body.append('cartao', formData.cartaoNome);
    if (formData.cartaoFinal) {
      body.append('final_cartao', formData.cartaoFinal);
    }
  }
  
  const response = await fetchWithAuth(`${BASE_URL}/upload/preview`, {
    method: 'POST',
    body
  });
  
  if (!response.ok) {
    let errorDetail = 'Erro ao fazer upload do arquivo'
    try {
      const error = await response.json();
      errorDetail = error.detail || errorDetail
    } catch (e) {
      const errorText = await response.text()
      errorDetail = errorText || errorDetail
    }
    throw new Error(errorDetail);
  }
  
  const data = await response.json();
  return { sessionId: data.sessionId };
}

/**
 * Busca dados de preview de uma sessão de upload
 */
export async function fetchPreviewData(sessionId: string): Promise<PreviewData> {
  const response = await fetchWithAuth(`${BASE_URL}/upload/preview/${sessionId}`);
  
  if (!response.ok) {
    throw new Error('Erro ao carregar dados do preview');
  }
  
  const data = await response.json();
  return data;
}
