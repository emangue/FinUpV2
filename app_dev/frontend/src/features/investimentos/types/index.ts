/**
 * Types para o domínio Investimentos
 */

export interface InvestimentoPortfolio {
  id: number
  user_id: number
  balance_id: string
  nome_produto: string
  corretora: string
  tipo_investimento: string
  classe_ativo?: string
  emissor?: string
  percentual_cdi?: number
  data_aplicacao?: string
  data_vencimento?: string
  quantidade: number
  valor_unitario_inicial?: string
  valor_total_inicial?: string
  /** Valores do histórico do mês (mesma fonte de ativos/passivos) - usar quando disponível */
  valor_total_mes?: string | number
  valor_unitario_mes?: string | number
  quantidade_mes?: number
  ativo: boolean
  created_at: string
  updated_at?: string
}

export interface InvestimentoHistorico {
  id: number
  investimento_id: number
  ano: number
  mes: number
  anomes: number
  data_referencia: string
  quantidade?: number
  valor_unitario?: string
  valor_total?: string
  aporte_mes?: string
  rendimento_mes?: string
  rendimento_acumulado?: string
  created_at: string
  updated_at?: string
}

export interface PortfolioResumo {
  total_investido: string
  valor_atual: string
  rendimento_total: string
  rendimento_percentual: number
  quantidade_produtos: number
  produtos_ativos: number
}

export interface RendimentoMensal {
  ano: number
  mes: number
  anomes: number
  rendimento_mes: string
  patrimonio_final: string
  aporte_mes: string
}

export interface PatrimonioMensal {
  ano: number
  mes: number
  anomes: number
  ativos: number
  passivos: number
  patrimonio_liquido: number
}

export interface InvestimentoCenario {
  id: number
  user_id: number
  nome_cenario: string
  descricao?: string
  patrimonio_inicial: string
  rendimento_mensal_pct: string
  aporte_mensal: string
  periodo_meses: number
  ativo: boolean
  created_at: string
  updated_at?: string
  aportes_extraordinarios: AporteExtraordinario[]
  /** Sprint H: plano aposentadoria */
  idade_atual?: number
  idade_aposentadoria?: number
  renda_mensal_alvo?: string
  inflacao_aa?: string
  retorno_aa?: string
  anomes_inicio?: number
  principal?: boolean
  extras_json?: string
}

export interface AporteExtraordinario {
  id: number
  cenario_id: number
  mes_referencia: number
  valor: string
  descricao?: string
  created_at: string
}

export interface ProjecaoCenario {
  mes: number
  patrimonio: string
  rendimento_mes: string
  aporte_mes: string
  aporte_extraordinario: string
}

export interface SimulacaoCompleta {
  cenario: InvestimentoCenario
  projecoes: ProjecaoCenario[]
  patrimonio_final: string
  rendimento_total: string
  total_aportes: string
}

/**
 * Parâmetros para simulação de cenários
 */
export interface ParametrosSimulacao {
  taxaRendimentoAnual: number  // Taxa anual em %
  aporteMensal: number          // Valor mensal de aportes
  periodoMeses: number          // Período de projeção em meses
}

/**
 * Evolução mensal da simulação
 */
export interface EvolucaoMensal {
  mes: number
  ano: number
  patrimonio_total: number
  aportes_acumulados: number
  rendimentos_acumulados: number
  rentabilidade_percentual: number
}

/**
 * Resultado completo da simulação de cenário
 */
export interface SimulacaoCenario {
  patrimonio_inicial: number
  patrimonio_final: number
  total_aportes: number
  total_rendimentos: number
  patrimonio_medio_ponderado: number
  evolucao_mensal: EvolucaoMensal[]
  projecao_mensal?: Array<{
    mes: number
    mes_real: number
    ano_real: number
    patrimonio: number
    aportes_acumulados: number
  }>
}

export interface DistribuicaoTipo {
  tipo: string
  quantidade: number
  total_investido: string
}

// Filtros
export interface InvestimentosFilters {
  tipo_investimento?: string
  ativo?: boolean
  anomes?: number
  skip?: number
  limit?: number
}

export interface TimelineFilters {
  ano_inicio: number
  ano_fim: number
}

// Forms
export interface CreateInvestimentoForm {
  balance_id: string
  nome_produto: string
  corretora: string
  tipo_investimento: string
  classe_ativo?: string
  emissor?: string
  ano?: number
  anomes?: number
  percentual_cdi?: number
  data_aplicacao?: string
  data_vencimento?: string
  quantidade?: number
  valor_unitario_inicial?: number
  valor_total_inicial?: number
}

export interface CreateCenarioForm {
  nome_cenario: string
  descricao?: string
  patrimonio_inicial: number
  rendimento_mensal_pct: number
  aporte_mensal: number
  periodo_meses: number
  aportes_extraordinarios?: Array<{
    mes_referencia: number
    valor: number
    descricao?: string
  }>
  /** Sprint H: plano aposentadoria */
  idade_atual?: number
  idade_aposentadoria?: number
  renda_mensal_alvo?: number
  inflacao_aa?: number
  retorno_aa?: number
  anomes_inicio?: number
  principal?: boolean
  extras_json?: string
}

export interface UpdateCenarioForm {
  nome_cenario?: string
  descricao?: string
  patrimonio_inicial?: number
  rendimento_mensal_pct?: number
  aporte_mensal?: number
  periodo_meses?: number
  idade_atual?: number
  idade_aposentadoria?: number
  renda_mensal_alvo?: number
  inflacao_aa?: number
  retorno_aa?: number
  anomes_inicio?: number
  principal?: boolean
  extras_json?: string
}

export interface ProjecaoItem {
  mes_num: number
  anomes: number
  patrimonio: number
  /** Aporte planejado do mês (regular + extraordinário) - usado como meta/plano */
  aporte: number
}
