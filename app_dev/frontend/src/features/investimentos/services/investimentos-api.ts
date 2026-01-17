/**
 * API Service para Investimentos
 */

import { API_CONFIG } from '@/core/config/api.config'
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

// Usar proxy do Next.js - ele já adiciona /api/v1
const BASE_URL = `/api/investimentos`

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
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error('Erro ao buscar investimentos')
  }
  
  return response.json()
}

export async function getInvestimento(id: number): Promise<InvestimentoPortfolio> {
  const response = await fetch(`${BASE_URL}/${id}`)
  
  if (!response.ok) {
    throw new Error('Erro ao buscar investimento')
  }
  
  return response.json()
}

export async function createInvestimento(
  data: CreateInvestimentoForm
): Promise<InvestimentoPortfolio> {
  const response = await fetch(BASE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    throw new Error('Erro ao criar investimento')
  }
  
  return response.json()
}

export async function updateInvestimento(
  id: number,
  data: Partial<CreateInvestimentoForm>
): Promise<InvestimentoPortfolio> {
  const response = await fetch(`${BASE_URL}/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    throw new Error('Erro ao atualizar investimento')
  }
  
  return response.json()
}

export async function deleteInvestimento(id: number): Promise<void> {
  const response = await fetch(`${BASE_URL}/${id}`, {
    method: 'DELETE',
  })
  
  if (!response.ok) {
    throw new Error('Erro ao deletar investimento')
  }
}

/**
 * Portfolio Analytics
 */
export async function getPortfolioResumo(): Promise<PortfolioResumo> {
  const response = await fetch(`${BASE_URL}/resumo`)
  
  if (!response.ok) {
    throw new Error('Erro ao buscar resumo do portfólio')
  }
  
  return response.json()
}

export async function getDistribuicaoPorTipo(): Promise<DistribuicaoTipo[]> {
  const response = await fetch(`${BASE_URL}/distribuicao-tipo`)
  
  if (!response.ok) {
    throw new Error('Erro ao buscar distribuição por tipo')
  }
  
  return response.json()
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
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error('Erro ao buscar histórico')
  }
  
  return response.json()
}

export async function getRendimentosTimeline(
  filters: TimelineFilters
): Promise<RendimentoMensal[]> {
  const params = new URLSearchParams({
    ano_inicio: String(filters.ano_inicio),
    ano_fim: String(filters.ano_fim),
  })

  const url = `${BASE_URL}/timeline/rendimentos?${params.toString()}`
  const response = await fetch(url)
  
  if (!response.ok) {
    throw new Error('Erro ao buscar timeline de rendimentos')
  }
  
  return response.json()
}

/**
 * Cenários
 */
export async function getCenarios(ativo?: boolean): Promise<InvestimentoCenario[]> {
  const params = new URLSearchParams()
  if (ativo !== undefined) params.append('ativo', String(ativo))

  const url = `${BASE_URL}/cenarios?${params.toString()}`
  const response = await fetch(url)
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || errorData.message || 'Erro ao criar cenário')
  }
  
  return response.json()
}

export async function createCenario(
  data: CreateCenarioForm
): Promise<InvestimentoCenario> {
  const response = await fetch(`${BASE_URL}/cenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || errorData.message || 'Erro ao criar cenário')
  }

  return response.json()
}

export async function simularCenario(cenarioId: number): Promise<SimulacaoCompleta> {
  const response = await fetch(`${BASE_URL}/cenarios/${cenarioId}/simular`)
  
  if (!response.ok) {
    throw new Error('Erro ao simular cenário')
  }
  
  return response.json()
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
  
  for (let mes = 1; mes <= periodoMeses; mes++) {
    patrimonio = (patrimonio + aporteMensal) * (1 + taxaMensal)
    projecao.push({
      mes,
      patrimonio: Math.round(patrimonio * 100) / 100,
      aportes_acumulados: aporteMensal * mes,
      rendimentos_acumulados: patrimonio - (aporteMensal * mes)
    })
  }
  
  const totalAportes = aporteMensal * periodoMeses
  const totalRendimentos = patrimonio - totalAportes
  
  return {
    patrimonio_inicial: 0,
    patrimonio_final: Math.round(patrimonio * 100) / 100,
    total_aportes: totalAportes,
    total_rendimentos: Math.round(totalRendimentos * 100) / 100,
    rentabilidade_percentual: totalAportes > 0 ? (totalRendimentos / totalAportes) * 100 : 0,
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
  const response = await fetch(`${BASE_URL}/cenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || errorData.message || 'Erro ao criar cenário')
  }

  return response.json()
}

/**
 * Lista cenários salvos
 */
export async function listarCenarios(ativo: boolean = true): Promise<any[]> {
  const response = await fetch(`${BASE_URL}/cenarios?ativo=${ativo}`)

  if (!response.ok) {
    throw new Error('Erro ao listar cenários')
  }

  return response.json()
}

/**
 * Simula cenário salvo no banco
 */
export async function simularCenarioSalvo(cenarioId: number): Promise<any> {
  const response = await fetch(`${BASE_URL}/cenarios/${cenarioId}/simular`)

  if (!response.ok) {
    throw new Error('Erro ao simular cenário salvo')
  }

  return response.json()
}
