/**
 * API Service para Investimentos
 * 
 * 🔐 FASE 1 - Isolamento de Dados:
 * Agora usa fetchWithAuth() para enviar token JWT automaticamente
 */

import { apiGet, apiPost, apiPatch, apiDelete } from '@/core/config/api.config'
import type {
  InvestimentoPortfolio,
  PortfolioResumo,
  RendimentoMensal,
  InvestimentoCenario,
  SimulacaoCompleta,
  DistribuicaoTipo,
  InvestimentosFilters,
  TimelineFilters,
  CreateInvestimentoForm,
  CreateCenarioForm,
  InvestimentoHistorico,
  ParametrosSimulacao,
  SimulacaoCenario,
} from '../types'

// URL completa para investimentos
const BASE_URL = `/api/v1/investimentos`

/**
 * Portfolio Endpoints
 */
export async function getInvestimentos(
  filters?: InvestimentosFilters
): Promise<InvestimentoPortfolio[]> {
  const params = new URLSearchParams()
  
  if (filters?.tipo_investimento) params.append('tipo_investimento', filters.tipo_investimento)
  if (filters?.ativo !== undefined) params.append('ativo', String(filters.ativo))
  if (filters?.skip) params.append('skip', String(filters.skip))
  if (filters?.limit) params.append('limit', String(filters.limit))

  const url = `${BASE_URL}?${params.toString()}`
  return apiGet<InvestimentoPortfolio[]>(url)
}

export async function getInvestimento(id: number): Promise<InvestimentoPortfolio> {
  return apiGet<InvestimentoPortfolio>(`${BASE_URL}/${id}`)
}

export async function createInvestimento(
  data: CreateInvestimentoForm
): Promise<InvestimentoPortfolio> {
  return apiPost<InvestimentoPortfolio>(BASE_URL, data)
}

export async function updateInvestimento(
  id: number,
  data: Partial<CreateInvestimentoForm>
): Promise<InvestimentoPortfolio> {
  return apiPatch<InvestimentoPortfolio>(`${BASE_URL}/${id}`, data)
}

export async function deleteInvestimento(id: number): Promise<void> {
  await apiDelete<void>(`${BASE_URL}/${id}`)
}

/**
 * Portfolio Analytics
 */
export async function getPortfolioResumo(): Promise<PortfolioResumo> {
  return apiGet<PortfolioResumo>(`${BASE_URL}/resumo`)
}

export async function getDistribuicaoPorTipo(): Promise<DistribuicaoTipo[]> {
  return apiGet<DistribuicaoTipo[]>(`${BASE_URL}/distribuicao-tipo`)
}

/**
 * Histórico
 */
export async function getHistoricoInvestimento(
  investimentoId: number,
  filters?: { ano_inicio?: number; ano_fim?: number }
): Promise<InvestimentoHistorico[]> {
  const params = new URLSearchParams()
  
  if (filters?.ano_inicio) params.append('ano_inicio', String(filters.ano_inicio))
  if (filters?.ano_fim) params.append('ano_fim', String(filters.ano_fim))

  const url = `${BASE_URL}/${investimentoId}/historico?${params.toString()}`
  return apiGet<InvestimentoHistorico[]>(url)
}

export async function getRendimentosTimeline(
  filters: TimelineFilters
): Promise<RendimentoMensal[]> {
  const params = new URLSearchParams({
    ano_inicio: String(filters.ano_inicio),
    ano_fim: String(filters.ano_fim),
  })

  const url = `${BASE_URL}/timeline/rendimentos?${params.toString()}`
  return apiGet<RendimentoMensal[]>(url)
}

/**
 * Cenários
 */
export async function getCenarios(ativo?: boolean): Promise<InvestimentoCenario[]> {
  const params = new URLSearchParams()
  if (ativo !== undefined) params.append('ativo', String(ativo))

  const url = `${BASE_URL}/cenarios?${params.toString()}`
  return apiGet<InvestimentoCenario[]>(url)
}

export async function createCenario(
  data: CreateCenarioForm
): Promise<InvestimentoCenario> {
  return apiPost<InvestimentoCenario>(`${BASE_URL}/cenarios`, data)
}

export async function simularCenario(cenarioId: number): Promise<SimulacaoCompleta> {
  return apiGet<SimulacaoCompleta>(`${BASE_URL}/cenarios/${cenarioId}/simular`)
}

/**
 * Simula cenário personalizado (rápido, sem salvar no banco)
 * Faz cálculos locais no frontend
 */
export async function simularCenarioPersonalizado(
  parametros: ParametrosSimulacao
): Promise<SimulacaoCenario> {
  // Calcular simulação localmente (não precisa backend para simulação rápida)
  const { taxaRendimentoAnual, aporteMensal, periodoMeses } = parametros
  const taxaMensal = Math.pow(1 + taxaRendimentoAnual / 100, 1/12) - 1
  
  let patrimonio = 0
  const projecao = []
  const hoje = new Date()
  const mesAtual = hoje.getMonth() + 1
  const anoAtual = hoje.getFullYear()
  
  for (let mes = 1; mes <= periodoMeses; mes++) {
    patrimonio = (patrimonio + aporteMensal) * (1 + taxaMensal)
    
    // Calcular mês/ano real da projeção
    const mesesTotais = (anoAtual * 12 + mesAtual - 1) + mes
    const mes_real = (mesesTotais % 12) + 1
    const ano_real = Math.floor(mesesTotais / 12)
    
    projecao.push({
      mes,
      mes_real,
      ano_real,
      patrimonio: Math.round(patrimonio * 100) / 100,
      aportes_acumulados: aporteMensal * mes
    })
  }
  
  const totalAportes = aporteMensal * periodoMeses
  const totalRendimentos = patrimonio - totalAportes
  
  return {
    patrimonio_inicial: 0,
    patrimonio_final: Math.round(patrimonio * 100) / 100,
    total_aportes: totalAportes,
    total_rendimentos: Math.round(totalRendimentos * 100) / 100,
    patrimonio_medio_ponderado: 0, // Placeholder
    evolucao_mensal: [],
    projecao_mensal: projecao
  }
}

/**
 * Cria e salva cenário no banco de dados
 */
export async function criarCenario(data: {
  nome_cenario: string
  descricao?: string
  patrimonio_inicial: number
  rendimento_mensal_pct: number
  aporte_mensal: number
  periodo_meses: number
}): Promise<any> {
  // ✅ FASE 1 - Autenticação automática via apiPost
  return apiPost<any>(`${BASE_URL}/cenarios`, data)
}

/**
 * Lista cenários salvos
 */
export async function listarCenarios(ativo: boolean = true): Promise<any[]> {
  // ✅ FASE 1 - Autenticação automática via apiGet
  return apiGet<any[]>(`${BASE_URL}/cenarios?ativo=${ativo}`)
}

/**
 * Simula cenário salvo no banco
 */
export async function simularCenarioSalvo(cenarioId: number): Promise<any> {
  // ✅ FASE 1 - Autenticação automática via apiGet
  return apiGet<any>(`${BASE_URL}/cenarios/${cenarioId}/simular`)
}
