/**
 * API para Plano de Aposentadoria (Sprint H)
 * Usa investimentos/cenarios como backend
 */

import {
  createCenario,
  getCenario,
  updateCenario,
  getCenarios,
  getCenarioProjecao,
} from '@/features/investimentos/services/investimentos-api'
import type { InvestimentoCenario, ProjecaoItem } from '@/features/investimentos/types'
import type { AporteExtraordinario } from '../types'

export type PlanoPayload = {
  age: number
  retire: number
  patrimonio: number
  rendaMensal: number
  aporte: number
  retorno: number
  inflacao: number
  extras: AporteExtraordinario[]
  nomeCenario?: string
}

function toExtrasJson(extras: AporteExtraordinario[]): string {
  return JSON.stringify(
    extras.map((e) => ({
      mesAno: e.mesAno,
      valor: e.valor,
      descricao: e.descricao,
      recorrencia: e.recorrencia,
      evoluir: e.evoluir,
      evolucaoValor: e.evolucaoValor,
      evolucaoTipo: e.evolucaoTipo,
    }))
  )
}

function parseExtrasJson(jsonStr: string | undefined): AporteExtraordinario[] {
  if (!jsonStr) return []
  try {
    const arr = JSON.parse(jsonStr)
    if (!Array.isArray(arr)) return []
    return arr.map((e: Record<string, unknown>, i: number) => ({
      id: `e${i}-${Date.now()}`,
      mesAno: (e.mesAno as number) ?? (e.mes_referencia as number) ?? 12,
      valor: (e.valor as number) ?? 0,
      descricao: (e.descricao as string) ?? '',
      recorrencia: (e.recorrencia as AporteExtraordinario['recorrencia']) ?? 'unico',
      evoluir: (e.evoluir as boolean) ?? false,
      evolucaoValor: (e.evolucaoValor as number) ?? 0,
      evolucaoTipo: (e.evolucaoTipo as 'percentual' | 'nominal') ?? 'percentual',
    }))
  } catch {
    return []
  }
}

/** Converte retorno a.a. para taxa mensal */
export function retornoAaToMensal(retornoAa: number): number {
  return Math.pow(1 + retornoAa / 100, 1 / 12) - 1
}

/** Próximo mês (aportes começam no mês seguinte ao patrimônio) */
function nextAnomes(anomes: number): number {
  const ano = Math.floor(anomes / 100)
  const mes = anomes % 100
  if (mes < 12) return ano * 100 + mes + 1
  return (ano + 1) * 100 + 1
}

export async function salvarPlano(
  payload: PlanoPayload,
  patrimonioLiquido: number,
  /** anomes do patrimônio usado (ex: 202601). Aportes começam no mês seguinte */
  anomesPatrimonio?: number
): Promise<InvestimentoCenario> {
  const periodoMeses = Math.max(1, (payload.retire - payload.age) * 12)
  const rendimentoMensalPct = retornoAaToMensal(payload.retorno)
  const ano = new Date().getFullYear()
  const anomesInicio = anomesPatrimonio != null
    ? nextAnomes(anomesPatrimonio)
    : ano * 100 + 1

  return createCenario({
    nome_cenario: payload.nomeCenario ?? `Plano ${ano}`,
    patrimonio_inicial: patrimonioLiquido > 0 ? patrimonioLiquido : payload.patrimonio,
    rendimento_mensal_pct: rendimentoMensalPct,
    aporte_mensal: payload.aporte,
    periodo_meses: periodoMeses,
    idade_atual: payload.age,
    idade_aposentadoria: payload.retire,
    renda_mensal_alvo: payload.rendaMensal,
    inflacao_aa: payload.inflacao,
    retorno_aa: payload.retorno,
    anomes_inicio: anomesInicio,
    principal: true,
    extras_json: toExtrasJson(payload.extras),
    aportes_extraordinarios: [],
  })
}

export async function atualizarPlano(
  cenarioId: number,
  payload: PlanoPayload,
  patrimonioLiquido: number,
  /** anomes do patrimônio usado (ex: 202601). Aportes começam no mês seguinte */
  anomesPatrimonio?: number
): Promise<InvestimentoCenario> {
  const periodoMeses = Math.max(1, (payload.retire - payload.age) * 12)
  const rendimentoMensalPct = retornoAaToMensal(payload.retorno)
  const ano = new Date().getFullYear()
  const anomesInicio = anomesPatrimonio != null
    ? nextAnomes(anomesPatrimonio)
    : ano * 100 + 1

  return updateCenario(cenarioId, {
    nome_cenario: payload.nomeCenario,
    patrimonio_inicial: patrimonioLiquido > 0 ? patrimonioLiquido : payload.patrimonio,
    rendimento_mensal_pct: rendimentoMensalPct,
    aporte_mensal: payload.aporte,
    periodo_meses: periodoMeses,
    idade_atual: payload.age,
    idade_aposentadoria: payload.retire,
    renda_mensal_alvo: payload.rendaMensal,
    inflacao_aa: payload.inflacao,
    retorno_aa: payload.retorno,
    anomes_inicio: anomesInicio,
    principal: true,
    extras_json: toExtrasJson(payload.extras),
  })
}

export async function carregarPlano(cenarioId: number): Promise<{
  cenario: InvestimentoCenario
  age: number
  retire: number
  patrimonio: number
  rendaMensal: number
  aporte: number
  retorno: number
  inflacao: number
  extras: AporteExtraordinario[]
}> {
  const c = await getCenario(cenarioId)
  const patrimonio = parseFloat(String(c.patrimonio_inicial)) || 0
  const rendaMensal = c.renda_mensal_alvo ? parseFloat(String(c.renda_mensal_alvo)) : 25000
  const aporte = parseFloat(String(c.aporte_mensal)) || 0
  const retorno = c.retorno_aa ? parseFloat(String(c.retorno_aa)) : 10
  const inflacao = c.inflacao_aa ? parseFloat(String(c.inflacao_aa)) : 4.5
  const extras = parseExtrasJson(c.extras_json)

  return {
    cenario: c,
    age: c.idade_atual ?? 35,
    retire: c.idade_aposentadoria ?? 65,
    patrimonio,
    rendaMensal,
    aporte,
    retorno,
    inflacao,
    extras,
  }
}

export { getCenarios, getCenarioProjecao }
export type { InvestimentoCenario, ProjecaoItem }
