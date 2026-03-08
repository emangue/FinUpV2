/**
 * API client do domínio Plano (05-plano-financeiro)
 * Sprint 6: Renda, Orçamento (volta ao legado — sem compromissos)
 */
import { fetchWithAuth } from '@/core/utils/api-client';
import { API_CONFIG } from '@/core/config/api.config';
import { getCached, setCached, getInFlight, setInFlight } from '@/core/utils/in-memory-cache';

const TTL_2MIN = 2 * 60 * 1000;
const TTL_5MIN = 5 * 60 * 1000;

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
  const key = `plano:resumo:${ano}:${mes}`;
  const cached = getCached<ResumoPlanoResponse>(key);
  if (cached) return cached;
  let inFlight = getInFlight<ResumoPlanoResponse>(key);
  if (!inFlight) {
    inFlight = fetchWithAuth(`${BASE}/resumo?ano=${ano}&mes=${mes}`)
      .then(res => { if (!res.ok) throw new Error('Erro ao carregar resumo'); return res.json(); })
      .then(data => { setCached(key, data, TTL_2MIN); return data; });
    setInFlight(key, inFlight);
  }
  return inFlight;
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
  const key = `plano:orcamento:${ano}:${mes}`;
  const cached = getCached<OrcamentoItem[]>(key);
  if (cached) return cached;
  let inFlight = getInFlight<OrcamentoItem[]>(key);
  if (!inFlight) {
    inFlight = fetchWithAuth(`${BASE}/orcamento?ano=${ano}&mes=${mes}`)
      .then(res => { if (!res.ok) throw new Error('Erro ao carregar orçamento'); return res.json(); })
      .then(data => { setCached(key, data, TTL_2MIN); return data; });
    setInFlight(key, inFlight);
  }
  return inFlight;
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
  const key = `plano:impacto:${ano}:${mes}`;
  const cached = getCached<ImpactoLongoPrazoResponse>(key);
  if (cached) return cached;
  let inFlight = getInFlight<ImpactoLongoPrazoResponse>(key);
  if (!inFlight) {
    inFlight = fetchWithAuth(`${BASE}/impacto-longo-prazo?ano=${ano}&mes=${mes}`)
      .then(res => { if (!res.ok) throw new Error('Erro ao carregar impacto'); return res.json(); })
      .then(data => { setCached(key, data, TTL_5MIN); return data; });
    setInFlight(key, inFlight);
  }
  return inFlight;
}

// ─── Cashflow e Projeção (Fase 2) ───────────────────────────────────────────

export interface CashflowMes {
  mes_referencia: string;
  renda_esperada: number;
  renda_realizada?: number | null;
  renda_usada?: number;
  gastos_recorrentes: number;
  gastos_usados?: number;
  total_gastos?: number;                 // gastos_recorrentes + debitos_extras
  investimentos_realizados?: number | null;
  aporte_usado?: number;                  // = renda_usada - total_gastos (o que sobra para investir)
  gastos_extras_esperados: number;
  extras_creditos?: number;               // receitas extraordinárias do mês
  extras_debitos?: number;                // despesas extraordinárias do mês
  gastos_realizados: number | null;
  aporte_planejado: number;               // valor fixo do wizard (referência)
  saldo_projetado: number | null;         // @deprecated — alias de aporte_usado
  status_mes: 'ok' | 'parcial' | 'futuro' | 'negativo';
  use_realizado?: boolean;
  grupos: unknown[];
  expectativas: unknown[];
}

export interface CashflowResponse {
  ano: number;
  nudge_acumulado: number;
  meses: CashflowMes[];
}

export async function getCashflow(ano: number): Promise<CashflowResponse> {
  const key = `plano:cashflow:${ano}`;
  const cached = getCached<CashflowResponse>(key);
  if (cached) return cached;
  let inFlight = getInFlight<CashflowResponse>(key);
  if (!inFlight) {
    inFlight = fetchWithAuth(`${BASE}/cashflow?ano=${ano}`)
      .then(res => { if (!res.ok) throw new Error('Erro ao carregar cashflow'); return res.json(); })
      .then(data => { setCached(key, data, TTL_2MIN); return data; });
    setInFlight(key, inFlight);
  }
  return inFlight;
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
  reducao_pct?: number,
  sem_patrimonio?: boolean
): Promise<ProjecaoResponse> {
  const params = new URLSearchParams({ ano: String(ano) });
  if (meses != null) params.set('meses', String(meses));
  if (reducao_pct != null) params.set('reducao_pct', String(reducao_pct));
  if (sem_patrimonio) params.set('sem_patrimonio', '1');
  const key = `plano:projecao:${ano}:${meses ?? ''}:${reducao_pct ?? 0}:${sem_patrimonio ? '1' : '0'}`;
  const cached = getCached<ProjecaoResponse>(key);
  if (cached) return cached;
  let inFlight = getInFlight<ProjecaoResponse>(key);
  if (!inFlight) {
    inFlight = fetchWithAuth(`${BASE}/projecao?${params}`)
      .then(res => { if (!res.ok) throw new Error('Erro ao carregar projeção'); return res.json(); })
      .then(data => { setCached(key, data, TTL_5MIN); return data; });
    setInFlight(key, inFlight);
  }
  return inFlight;
}

export interface ProjecaoLongaItem {
  mes_num: number;
  ano: number;
  mes: number;
  patrimonio_nominal: number;
  patrimonio_real: number;
  aporte_mes: number;
}

export interface ProjecaoLongaResponse {
  patrimonio_inicial: number;
  patrimonio_final_nominal: number;
  patrimonio_final_real: number;
  meses: number;
  serie: ProjecaoLongaItem[];
}

export async function getProjecaoLonga(
  inflacao_pct?: number
): Promise<ProjecaoLongaResponse> {
  const params = new URLSearchParams();
  if (inflacao_pct != null) params.set('inflacao_pct', String(inflacao_pct));
  const res = await fetchWithAuth(`${BASE}/projecao-longa?${params}`);
  if (!res.ok) throw new Error('Erro ao carregar projeção longa');
  return res.json();
}

export interface GrupoMedia3Meses {
  grupo: string;
  valor_planejado: number;
  valor_medio_3_meses: number;
}

export async function getGruposMedia3Meses(
  ano: number,
  mes: number
): Promise<GrupoMedia3Meses[]> {
  const res = await fetchWithAuth(`${BASE}/grupos-media-3-meses?ano=${ano}&mes=${mes}`);
  if (!res.ok) throw new Error('Erro ao carregar grupos');
  return res.json();
}

const BASE_BUDGET = `${API_CONFIG.BACKEND_URL}/api/v1/budget`;

/** Salva metas em bulk via budget/planning (mes_referencia + budgets) */
export async function putOrcamentoBulk(
  mes_referencia: string,
  budgets: { grupo: string; valor_planejado: number }[]
): Promise<unknown[]> {
  const res = await fetchWithAuth(`${BASE_BUDGET}/planning/bulk-upsert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mes_referencia, budgets }),
  });
  if (!res.ok) throw new Error('Erro ao salvar metas');
  return res.json();
}

const MESES_LABEL = ['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'];

/** Retorna { count, mesFimLabel } de mes_inicio até hoje+12 meses */
export function getOrcamentoRangeInfo(mes_inicio: string): { count: number; mesFimLabel: string } {
  const hoje = new Date();
  const mesFim = new Date(hoje.getFullYear(), hoje.getMonth() + 12, 1);
  const mesFimStr = `${mesFim.getFullYear()}-${String(mesFim.getMonth() + 1).padStart(2, '0')}`;
  const [yFim, mFim] = mesFimStr.split('-').map(Number);
  const mesFimLabel = `${MESES_LABEL[mFim - 1]}/${yFim}`;
  const [y1, m1] = mes_inicio.split('-').map(Number);
  let count = 0;
  let y = y1, m = m1;
  while (y < yFim || (y === yFim && m <= mFim)) {
    count++;
    m += 1;
    if (m > 12) { m = 1; y += 1; }
  }
  return { count, mesFimLabel };
}

/** Aplica metas de mes_inicio até hoje+12 meses em budget_planning */
export async function putOrcamentoBulkRange(
  mes_inicio: string,
  budgets: { grupo: string; valor_planejado: number }[]
): Promise<void> {
  const hoje = new Date();
  const mesFim = new Date(hoje.getFullYear(), hoje.getMonth() + 12, 1);
  const mesFimStr = `${mesFim.getFullYear()}-${String(mesFim.getMonth() + 1).padStart(2, '0')}`;
  const [y1, m1] = mes_inicio.split('-').map(Number);
  const [y2, m2] = mesFimStr.split('-').map(Number);
  const meses: string[] = [];
  let y = y1, m = m1;
  while (y < y2 || (y === y2 && m <= m2)) {
    meses.push(`${y}-${String(m).padStart(2, '0')}`);
    m += 1;
    if (m > 12) { m = 1; y += 1; }
  }
  for (const mesRef of meses) {
    await putOrcamentoBulk(mesRef, budgets);
  }
}

export interface PerfilResponse {
  renda_mensal_liquida: number | null;
  aporte_planejado: number | null;
  idade_atual: number | null;
  idade_aposentadoria: number | null;
  patrimonio_atual: number | null;
  taxa_retorno_anual: number | null;
  crescimento_renda: number | null;
  reajuste_mes: number | null;
  reajuste_ano: number | null;
  crescimento_gastos: number | null;
}

export interface PerfilUpdatePayload {
  renda_mensal_liquida?: number;
  aporte_planejado?: number;
  idade_atual?: number;
  idade_aposentadoria?: number;
  patrimonio_atual?: number;
  taxa_retorno_anual?: number;
  crescimento_renda?: number;
  reajuste_mes?: number;
  reajuste_ano?: number;
  crescimento_gastos?: number;
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

/** Grupos Despesa para vincular gastos sazonais (planning + excepcional por grupo) */
export async function getGruposDespesa(): Promise<string[]> {
  const res = await fetchWithAuth(`${BASE_BUDGET}/planning/grupos-com-categoria`);
  if (!res.ok) return [];
  const data: { nome_grupo: string; categoria_geral: string }[] = await res.json();
  return data.filter((g) => g.categoria_geral === 'Despesa').map((g) => g.nome_grupo);
}

export interface ExpectativaItem {
  id: number;
  descricao: string | null;
  valor: number;
  grupo: string | null;
  tipo_lancamento: string;
  mes_referencia: string;
  tipo_expectativa: string;
  status: string;
  recorrencia?: string;
  parcelas?: number;
  evoluir?: boolean;
  evolucaoValor?: number;
  evolucaoTipo?: 'percentual' | 'nominal';
}

export interface ExpectativaCreatePayload {
  descricao: string;
  valor: number;
  mes_referencia: string; // YYYY-MM
  grupo?: string;
  subgrupo?: string;
  tipo_lancamento?: 'debito' | 'credito';
  tipo_expectativa?: 'sazonal_plano' | 'renda_plano' | 'parcela_futura';
  recorrencia?: 'unico' | 'bimestral' | 'trimestral' | 'semestral' | 'anual';
  parcelas?: number; // 1 = à vista, 2-24 = parcelado
  evoluir?: boolean;
  evolucaoValor?: number;
  evolucaoTipo?: 'percentual' | 'nominal';
}

export async function getExpectativas(mes?: string): Promise<ExpectativaItem[]> {
  const url = mes ? `${BASE}/expectativas?mes=${mes}` : `${BASE}/expectativas`;
  const res = await fetchWithAuth(url);
  if (!res.ok) throw new Error('Erro ao listar expectativas');
  return res.json();
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
      subgrupo: payload.subgrupo ?? null,
      tipo_lancamento: payload.tipo_lancamento ?? 'debito',
      tipo_expectativa: payload.tipo_expectativa ?? 'sazonal_plano',
      recorrencia: payload.recorrencia ?? 'unico',
      parcelas: payload.parcelas ?? 1,
      evoluir: payload.evoluir ?? false,
      evolucao_valor: payload.evolucaoValor ?? 0,
      evolucao_tipo: payload.evolucaoTipo ?? 'percentual',
    }),
  });
  if (!res.ok) throw new Error('Erro ao criar expectativa');
  return res.json();
}

export async function putExpectativa(
  expectativaId: number,
  payload: ExpectativaCreatePayload
): Promise<ExpectativaItem> {
  const res = await fetchWithAuth(`${BASE}/expectativas/${expectativaId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      descricao: payload.descricao,
      valor: payload.valor,
      mes_referencia: payload.mes_referencia,
      grupo: payload.grupo ?? null,
      subgrupo: payload.subgrupo ?? null,
      tipo_lancamento: payload.tipo_lancamento ?? 'debito',
      tipo_expectativa: payload.tipo_expectativa ?? 'sazonal_plano',
      recorrencia: payload.recorrencia ?? 'unico',
      parcelas: payload.parcelas ?? 1,
      evoluir: payload.evoluir ?? false,
      evolucao_valor: payload.evolucaoValor ?? 0,
      evolucao_tipo: payload.evolucaoTipo ?? 'percentual',
    }),
  });
  if (!res.ok) throw new Error('Erro ao atualizar expectativa');
  return res.json();
}

export async function deleteExpectativa(expectativaId: number): Promise<void> {
  const res = await fetchWithAuth(`${BASE}/expectativas/${expectativaId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Erro ao excluir expectativa');
}
