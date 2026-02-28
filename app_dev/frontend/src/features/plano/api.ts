/**
 * API client do domínio Plano (05-plano-financeiro)
 * Sprint 6: Renda, Orçamento (volta ao legado — sem compromissos)
 */
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';

const BASE = `${API_CONFIG.BACKEND_URL}/api/v1/plano`;

export interface RendaResponse {
  renda: number | null;
}

export interface OrcamentoItem {
  grupo: string;
  gasto: number;
  meta: number | null;
  percentual: number | null;
  status: 'ok' | 'alerta' | 'excedido' | 'sem_meta';
}

export interface ResumoPlanoResponse {
  renda: number | null;
  total_budget: number;
  disponivel_real: number | null;
}

export async function getRenda(): Promise<RendaResponse> {
  const res = await fetchWithAuth(`${BASE}/renda`);
  if (!res.ok) throw new Error('Erro ao carregar renda');
  return res.json();
}

export async function getResumoPlano(ano: number, mes: number): Promise<ResumoPlanoResponse> {
  const res = await fetchWithAuth(`${BASE}/resumo?ano=${ano}&mes=${mes}`);
  if (!res.ok) throw new Error('Erro ao carregar resumo');
  return res.json();
}

export async function postRenda(renda_mensal_liquida: number): Promise<{ success: boolean; renda: number }> {
  const res = await fetchWithAuth(`${BASE}/renda`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ renda_mensal_liquida }),
  });
  if (!res.ok) throw new Error('Erro ao salvar renda');
  return res.json();
}

export async function getOrcamento(ano: number, mes: number): Promise<OrcamentoItem[]> {
  const res = await fetchWithAuth(`${BASE}/orcamento?ano=${ano}&mes=${mes}`);
  if (!res.ok) throw new Error('Erro ao carregar orçamento');
  return res.json();
}

export interface ImpactoLongoPrazoResponse {
  deficit_mensal?: number;
  custo_oportunidade_futuro?: number;
  anos_perdidos?: number;
  anos_restantes_para_aposentadoria?: number;
  mensagem?: string;
}

export async function getImpactoLongoPrazo(
  ano: number,
  mes: number
): Promise<ImpactoLongoPrazoResponse> {
  const res = await fetchWithAuth(`${BASE}/impacto-longo-prazo?ano=${ano}&mes=${mes}`);
  if (!res.ok) throw new Error('Erro ao carregar impacto');
  return res.json();
}
