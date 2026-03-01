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

// ─── Cashflow e Projeção (Fase 2) ───────────────────────────────────────────

export interface CashflowMes {
  mes_referencia: string;
  renda_esperada: number;
  renda_realizada?: number | null;
  renda_usada?: number;
  gastos_recorrentes: number;
  gastos_usados?: number;
  investimentos_realizados?: number | null;
  aporte_usado?: number; // = investimentos quando use_realizado
  gastos_extras_esperados: number;
  gastos_realizados: number | null;
  aporte_planejado: number;
  saldo_projetado: number | null;
  status_mes: 'ok' | 'parcial' | 'futuro' | 'negativo';
  grupos: unknown[];
  expectativas: unknown[];
}

export interface CashflowResponse {
  ano: number;
  nudge_acumulado: number;
  meses: CashflowMes[];
}

export async function getCashflow(ano: number): Promise<CashflowResponse> {
  const res = await fetchWithAuth(`${BASE}/cashflow?ano=${ano}`);
  if (!res.ok) throw new Error('Erro ao carregar cashflow');
  return res.json();
}

export interface CashflowDetalheMesResponse {
  mes_referencia: string;
  mes_fatura_filtro: string;
  formula: string;
  fonte_usada: string;
  total_realizado: number;
  total_planejado: number;
  valor_exibido_no_cashflow: number;
  qtd_transacoes: number;
  transacoes: Array<{
    id: number;
    estabelecimento: string;
    valor_original: number | null;
    valor_abs_usado: number;
    grupo: string;
    subgrupo: string;
    categoria_geral: string;
    mes_fatura: string | null;
    data: string | null;
  }>;
  soma_por_grupo: Array<{ grupo: string; total: number }>;
  planejado_por_grupo: Array<{ grupo: string; total: number }>;
}

export async function getCashflowDetalheMes(
  ano: number,
  mes: number
): Promise<CashflowDetalheMesResponse> {
  const res = await fetchWithAuth(`${BASE}/cashflow/detalhe-mes?ano=${ano}&mes=${mes}`);
  if (!res.ok) throw new Error('Erro ao carregar detalhes');
  return res.json();
}

export interface ProjecaoItem {
  mes: number;
  mes_referencia: string;
  saldo_mes: number;
  acumulado: number;
}

export interface ProjecaoResponse {
  patrimonio_inicial: number;
  reducao_pct: number;
  serie: ProjecaoItem[];
}

export async function getProjecao(
  ano: number,
  meses?: number,
  reducao_pct?: number
): Promise<ProjecaoResponse> {
  const params = new URLSearchParams({ ano: String(ano) });
  if (meses != null) params.set('meses', String(meses));
  if (reducao_pct != null) params.set('reducao_pct', String(reducao_pct));
  const res = await fetchWithAuth(`${BASE}/projecao?${params}`);
  if (!res.ok) throw new Error('Erro ao carregar projeção');
  return res.json();
}

export interface PerfilResponse {
  renda_mensal_liquida: number | null;
  aporte_planejado: number | null;
  idade_atual: number | null;
  idade_aposentadoria: number | null;
  patrimonio_atual: number | null;
  taxa_retorno_anual: number | null;
}

export interface PerfilUpdatePayload {
  renda_mensal_liquida?: number;
  aporte_planejado?: number;
  idade_atual?: number;
  idade_aposentadoria?: number;
  patrimonio_atual?: number;
  taxa_retorno_anual?: number;
}

export async function getPerfil(): Promise<PerfilResponse> {
  const res = await fetchWithAuth(`${BASE}/perfil`);
  if (!res.ok) throw new Error('Erro ao carregar perfil');
  return res.json();
}

export async function putPerfil(payload: PerfilUpdatePayload): Promise<PerfilUpdatePayload> {
  const res = await fetchWithAuth(`${BASE}/perfil`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Erro ao atualizar perfil');
  return res.json();
}

// ─── Expectativas (gastos/rendas extraordinárias) ────────────────────────────

export interface ExpectativaCreatePayload {
  descricao: string;
  valor: number;
  mes_referencia: string; // YYYY-MM
  grupo?: string;
  tipo_lancamento?: 'debito' | 'credito';
  tipo_expectativa?: 'sazonal_plano' | 'renda_plano' | 'parcela_futura';
}

export async function postExpectativa(payload: ExpectativaCreatePayload): Promise<{ id: number }> {
  const res = await fetchWithAuth(`${BASE}/expectativas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      descricao: payload.descricao,
      valor: payload.valor,
      mes_referencia: payload.mes_referencia,
      grupo: payload.grupo ?? null,
      tipo_lancamento: payload.tipo_lancamento ?? 'debito',
      tipo_expectativa: payload.tipo_expectativa ?? 'sazonal_plano',
    }),
  });
  if (!res.ok) throw new Error('Erro ao criar expectativa');
  return res.json();
}
